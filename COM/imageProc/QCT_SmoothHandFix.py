# Hisotry:
#   2017.05.08  Besler      Created
#
# Description:
#   Smooth hand segmentations
#
# Notes:
#   - Must use VTK 7.x
#   - Performs a dilation followed by erosion (background closing) and an inverted
#       connected components to smooth and guarantee a solid mask
#   - python ../../../../COM/imageProc/QCT_SmoothHandFix.py QCTCAL_0001_L_ISO_GOLD.nii QCTCAL_0001_L_ISO_GOLDFX.nii -n 3 -k 3
#   - python ../../../../COM/helperScripts/printSurfaceOverlap.py QCTCAL_0001_L_ISO_GOLD.nii QCTCAL_0001_L_ISO_GOLDFX.nii
#
# Usage:
#   $ python input.nii output.nii

# Libraries
import os
import argparse
import vtk

# Establish arguament parser to load the data
parser = argparse.ArgumentParser(
    description='Smooth a hand-segmented mask',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    'inputFilename',
    help='The input file name')
parser.add_argument(
    'outputFilename',
    help='The output file name')
parser.add_argument(
    '-k', '--kernelSize',
    default=int(3), type=int,
    help='Set to overwrite output without asking')
parser.add_argument(
    '-n', '--nThreads',
    default=1, type=int,
    help='Number of threads')
parser.add_argument(
    '-f', '--force',
    action='store_true',
    help='Set to overwrite output without asking')
args = parser.parse_args()

# Check that the input file exists
if not os.path.isfile(args.inputFilename):
    os.sys.exit('Input \"{inputFilename}\" does not exist! Exiting...'.format(inputFilename=args.inputFilename))

for filename in [args.inputFilename, args.outputFilename]:
    # Check that our output is of type NIfTI
    if not filename.lower().endswith('.nii'):
        os.sys.exit('Output \"{filename}\" is not of type *.nii! Exiting...'.format(filename=filename))

# Make sure we don't overwrite
if os.path.isfile(args.outputFilename):
    if not args.force:
        response = str(input('\"{outputFilename}\" exists. Overwrite? [Y/n]'.format(outputFilename=args.outputFilename)))
        if not 'yes'.startswith(response.lower()):
            os.sys.exit('Exiting to avoid overwrite...')

# Check kernel size
if args.kernelSize < 1:
    os.sys.exit('Kernel size must be one or greater. Exiting...')

# Check that the number of threads is valid
if args.nThreads < 1:
    os.sys.exit('Must have atleast one threads, asked for {}. Exiting...'.format(args.nThreads))

# Read input
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName(args.inputFilename)
print('Reading in \"{inputFilename}\"'.format(inputFilename=args.inputFilename))
reader.Update()

# Get scalar range for CC
scalarRange = reader.GetOutput().GetScalarRange()
tempPixelValue = 2
if tempPixelValue == scalarRange[1]:
    tempPixelValue = tempPixelValue + 1

# Make sure any floating points are removed (i.e. missed in segmentation)
cc = vtk.vtkImageConnectivityFilter()
cc.SetInputConnection(reader.GetOutputPort())
cc.SetExtractionModeToLargestRegion()
cc.SetScalarRange(scalarRange[1], scalarRange[1])
cc.SetLabelModeToConstantValue()
cc.SetLabelConstantValue(1)
print('Performing first connected component')
cc.Update()

# Dilate and erode (background-close) the image
dil = vtk.vtkImageContinuousDilate3D()
dil.SetInputConnection(cc.GetOutputPort())
dil.SetKernelSize(args.kernelSize,args.kernelSize,args.kernelSize)
dil.SetNumberOfThreads(args.nThreads)
print('Dilating with {} threads'.format(args.nThreads))
dil.Update()

ero = vtk.vtkImageContinuousErode3D()
ero.SetKernelSize(args.kernelSize,args.kernelSize,args.kernelSize)
ero.SetInputConnection(dil.GetOutputPort())
ero.SetNumberOfThreads(args.nThreads)
print('Eroding with {} threads'.format(args.nThreads))
ero.Update()

# Now perform a connected component on the background to get the largest image
ccBack = vtk.vtkImageConnectivityFilter()
ccBack.SetInputConnection(ero.GetOutputPort())
ccBack.SetExtractionModeToLargestRegion()
ccBack.SetScalarRange(0, 0)
ccBack.SetLabelModeToConstantValue()
ccBack.SetLabelConstantValue(tempPixelValue)
print('Performing connected component on background')
ccBack.Update()

# Invert the image back
math = vtk.vtkImageMathematics()
math.SetInputConnection(ccBack.GetOutputPort())
math.SetOperationToReplaceCByK()
math.SetConstantC(float(0))
math.SetConstantK(float(scalarRange[1]))
print('Setting mask to foreground...')
math.Update()

math2 = vtk.vtkImageMathematics()
math2.SetInputConnection(math.GetOutputPort())
math2.SetOperationToReplaceCByK()
math2.SetConstantC(float(tempPixelValue))
math2.SetConstantK(float(0))
print('Setting background to zero')
math2.Update()

# Mask must be a short for Elastix
caster = vtk.vtkImageCast()
caster.SetInputConnection(math2.GetOutputPort())
caster.SetOutputScalarTypeToShort()
caster.ClampOverflowOn()
print('Casting to short')
caster.Update()

# Write
writer = vtk.vtk.vtkNIFTIImageWriter()
writer.SetInputConnection(caster.GetOutputPort())
writer.SetFileName(args.outputFilename)
print('Writing to file {}'.format(args.outputFilename))
writer.Update()
