# History:
#   2017.04.12  babesler    Created
#
# Description:
#   Mask the bone region for registration
#
# Notes:
#   - Outputs a dilated mask around the bone
#
# Usage:
#   python QCT_BoneRegion.py input output lower upper

import vtk
import argparse
import os

# Setup and parse command line arguments
parser = argparse.ArgumentParser(description='Extract whole body mask',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('inputImage',
                    help='The input NIfTI (*.nii) image)')
parser.add_argument('outputImage',
                    help='The output NIfTI (*.nii) image)')
parser.add_argument('-t', '--threshold',
                    default=float(250),
                    help='The threshold for bone')
parser.add_argument('-k', '--kernelSize',
                    default=int(10),
                    help='The threshold for bone')
parser.add_argument('-f', '--force',
                    action='store_true',
                    help='Set to overwrite output without asking')
parser.add_argument('-n', '--nThreads',
                    default=1, type=int,
                    help='Number of threads')
args = parser.parse_args()

# Check that input file/dir exists
if not os.path.isfile(args.inputImage):
    os.sys.exit('Input file \"{inputImage}\" does not exist. Exiting...'.format(inputImage=args.inputImage))

# Check that output does not exist, or we can over write
for fileName in [args.inputImage, args.outputImage]:
    if not fileName.lower().endswith('.nii'):
        os.sys.exit('Output file \"{outputImage}\" is not a .nii file. Exiting...'.format(outputImage=fileName))
if os.path.isfile(args.outputImage):
    if not args.force:
        answer = raw_input('Output file \"{outputImage}\" exists. Overwrite? [Y/n]'.format(outputImage=args.outputImage))
        if str(answer).lower() not in set(['yes','y', 'ye', '']):
            os.sys.exit('Will not overwrite \"{inputFile}\". Exiting...'.
            format(inputFile=args.outputImage))

# Check that the number of threads is valid
if args.nThreads < 1:
    os.sys.exit('Must have atleast one threads, asked for {}. Exiting...'.format(args.nThreads))

# Set reader
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName(args.inputImage)
print("Loading data...")
reader.Update()
dimensions = reader.GetOutput().GetDimensions()
print("Loaded data with dimensions {dims}".format(dims=dimensions))

# Threshold
thresh = vtk.vtkImageThreshold()
thresh.SetInputConnection(reader.GetOutputPort())
thresh.ReplaceInOn()
thresh.ReplaceInOn()
thresh.ReplaceOutOn()
thresh.SetInValue(1.0)
thresh.SetOutValue(0.0)
thresh.ThresholdByUpper(float(args.threshold))
print('Thresholding at {}'.format(float(args.threshold)))
thresh.Update()

dil = vtk.vtkImageContinuousDilate3D()
dil.SetInputConnection(thresh.GetOutputPort())
dil.SetKernelSize(args.kernelSize, args.kernelSize, args.kernelSize)
dil.SetNumberOfThreads(args.nThreads)
print('Dilating...')
dil.Update()

# Extract largest Component
cc = vtk.vtkImageConnectivityFilter()
cc.SetInputConnection(dil.GetOutputPort())
cc.SetExtractionModeToLargestRegion()
cc.SetScalarRange(1,1)
print('Component labelling for bones')
cc.Update()

# Extract largest Component
cc2 = vtk.vtkImageConnectivityFilter()
cc2.SetInputConnection(cc.GetOutputPort())
cc2.SetExtractionModeToLargestRegion()
cc2.SetScalarRange(0,0)
cc2.SetLabelModeToConstantValue()
cc2.SetLabelConstantValue(2)
print('Component labelling for background')
cc2.Update()

# Set that stored 2 back to zero
math = vtk.vtkImageMathematics()
math.SetInputConnection(cc2.GetOutputPort())
math.SetOperationToReplaceCByK()
math.SetConstantC(float(0))
math.SetConstantK(float(1))
print('Setting bones to foreground...')
math.Update()

math2 = vtk.vtkImageMathematics()
math2.SetInputConnection(math.GetOutputPort())
math2.SetOperationToReplaceCByK()
math2.SetConstantC(float(2))
math2.SetConstantK(float(0))
print('Setting everything else to background...')
math2.Update()

# Writer
writer = vtk.vtkNIFTIImageWriter()
writer.SetFileName(args.outputImage)
writer.SetInputConnection(math2.GetOutputPort())
print("Writing to {}".format(args.outputImage))
writer.Update()
