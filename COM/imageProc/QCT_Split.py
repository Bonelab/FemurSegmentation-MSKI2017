# Hisotry:
#   2017.03.14  Besler      Created
#
# Description:
#   Subselect femurs from whole CT image
#
# Notes:
#   - Orientation: +z moves distal, +y moves anterior, +x moves left.

## Libraries
import os
import argparse
import vtk

## Establish arguament parser to load the data
parser = argparse.ArgumentParser(
    description='Split left and right femurs. The left femur is also transformed into a right femur',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    'inputImageFile',
    help='The input NIfTI (*.nii) image)')
parser.add_argument(
    'outputLeftFemurImageFile',
    help='Output NIfTI (*.nii) left femur file name')
parser.add_argument(
    'outputRightFemurImageFile',
    help='Output NIfTI (*.nii) right femur file name')
parser.add_argument(
    '-d', '--dim',
    default=float(0.5),
    type=float,
    help='Percent of axial distance to slice (between 0 and 1)')
parser.add_argument(
    '-f', '--force',
    action='store_true',
    help='Set to overwrite output without asking')
args = parser.parse_args()

## Check our inputs
# Check that the input is a directory
if not os.path.isfile(args.inputImageFile):
    os.sys.exit('Input \"{inputImageFile}\" does not exist! Exiting...'.format(inputImageFile=args.inputImageFile))

# Check that our output is of type NIfTI
for fileName in [args.inputImageFile, args.outputLeftFemurImageFile, args.outputRightFemurImageFile]:
    if not fileName.lower().endswith('.nii'):
        os.sys.exit('File \"{outputFilename}\" is not of type *.nii! Exiting...'.format(outputFilename=fileName))

# Make sure we don't overwrite
for fileName in [args.outputLeftFemurImageFile, args.outputRightFemurImageFile]:
    if os.path.isfile(fileName):
        if not args.force:
            response = str(raw_input('\"{outputFilename}\" exists. Overwrite? [Y/n]'.format(outputFilename=fileName)))
            if not 'yes'.startswith(response.lower()):
                os.sys.exit('Exiting to avoid overwrite...')

# Make sure our dimension is valid
if args.dim > 1 or args.dim < 0:
    os.sys.exit('Dimenion percentage \"{dim}\" is not in [0,1]'.format(dim=args.dim))

## Algorithm
# Read input
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName(args.inputImageFile)
print 'Reading in \"{fileName}\"'.format(fileName=args.inputImageFile)
reader.Update()

# Determine bounds (see: http://www.vtk.org/Wiki/VTK/Examples/Cxx/ImageData/ExtractVOI)
inputDims = reader.GetOutput().GetDimensions()
cutPoint = int(inputDims[0] * args.dim)
if cutPoint < 0:
    cutPoint = 0
if cutPoint > inputDims[0]:
    cutPoint = inputDims[0] - 2 # subtract 2 so there is a single x slice for left image.
rightVOI = [    0,          cutPoint,       0, inputDims[1]-1, 0, inputDims[2]-1]
leftVOI = [     cutPoint+1, inputDims[0]-1, 0, inputDims[1]-1, 0, inputDims[2]-1]
print "Percentage:       {dim}".format(dim=args.dim)
print "Input dimensions: {dims}".format(dims=inputDims)
print "Right VOI:        {VOI}".format(VOI=rightVOI)
print "Left VOI:         {VOI}".format(VOI=leftVOI)

# Extract left
rightExtractor = vtk.vtkExtractVOI()
rightExtractor.SetInputConnection(reader.GetOutputPort())
rightExtractor.SetVOI(rightVOI)
print 'Extractiong right subvolume'
rightExtractor.Update()

# Extract right
leftExtractor = vtk.vtkExtractVOI()
leftExtractor.SetInputConnection(reader.GetOutputPort())
leftExtractor.SetVOI(leftVOI)
print 'Extractiong left subvolume'
leftExtractor.Update()

# Flip image (left becomes right)
leftFlipper = vtk.vtkImageFlip()
leftFlipper.SetInputConnection(leftExtractor.GetOutputPort())
leftFlipper.SetFilteredAxis(0)
print 'Flipping left subvolume'
leftFlipper.Update()

# Write data out
rightWriter = vtk.vtkNIFTIImageWriter()
rightWriter.SetInputConnection(rightExtractor.GetOutputPort())
rightWriter.SetFileName(args.outputRightFemurImageFile)
print "Writing {fileName}".format(fileName=args.outputRightFemurImageFile)
rightWriter.Write()

leftWriter = vtk.vtkNIFTIImageWriter()
leftWriter.SetInputConnection(leftFlipper.GetOutputPort())
leftWriter.SetFileName(args.outputLeftFemurImageFile)
print "Writing {fileName}".format(fileName=args.outputLeftFemurImageFile)
leftWriter.Write()
