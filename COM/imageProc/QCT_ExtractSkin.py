# History:
#   2017.04.11  babesler    Created
#
# Description:
#   Mask the whole body in a CT scan
#
# Notes:
#   - This MUST be ran with vtk 7!!
#   - Outputs a mask of the body
#
# Usage:
#   python QCT_ExtractSkin.py input output lower upper

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
parser.add_argument('-l', '--lower',
                    default=None,
                    help='The lower bound for thresholding')
parser.add_argument('-u', '--upper',
                    default=float(-200),
                    help='The upper bound for thresholding')
parser.add_argument('-f', '--force',
                    action='store_true',
                    help='Set to overwrite output without asking')
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

if args.upper is None and args.lower is None:
    os.sys.exit('Atleast upper or lower must be specified. Exiting...')

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
if args.lower is None:
    thresh.ThresholdByUpper(float(args.upper))
elif args.upper is None:
    thresh.ThresholdByLower(float(args.lower))
else:
    thresh.ThresholdBetween(float(args.lower), float(args.upper))
print('Thresholding...')
thresh.Update()

# # Extract largest Component
# Need vtk 7.1 and won't have an affect on the result
# cc = vtk.vtkImageConnectivityFilter()
# cc.SetInputConnection(thresh.GetOutputPort())
# cc.SetExtractionModeToLargestRegion()
# print('Component labelling...')
# cc.Update()

# Writer
writer = vtk.vtkNIFTIImageWriter()
writer.SetFileName(args.outputImage)
#writer.SetInputConnection(cc.GetOutputPort())
writer.SetInputConnection(thresh.GetOutputPort())
print("Writing to {}".format(args.outputImage))
writer.Update()
