# History:
#   2017.04.06  babesler    Created
#
# Description:
#   Convert an image to short. This is needed for Elastix
#
# Notes:
#   - No range checking, because that seems like a pain
#   - Runs a connectivity filter over the image since MITK-GEM introduces weird
#       noise at the edge of images.
#
# Usage:
#   python QCT_ConvertToShort.py input output

import vtk
import argparse
import os

# Setup and parse command line arguments
parser = argparse.ArgumentParser(description='Subget medical data',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('inputImage',
                    help='The input NIfTI (*.nii) image)')
parser.add_argument('outputImage',
                    help='The output NIfTI (*.nii) image)')
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

# Set reader
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName(args.inputImage)
print("Loading data...")
reader.Update()
dimensions = reader.GetOutput().GetDimensions()
print("Loaded data with dimensions {dims}".format(dims=dimensions))

# Connected components
cc = vtk.vtkImageConnectivityFilter()
cc.SetInputConnection(reader.GetOutputPort())
cc.SetExtractionModeToLargestRegion()
cc.SetScalarRange(1,1)
print('Component labelling for bones')
cc.Update()

# Convert
caster = vtk.vtkImageCast()
caster.SetInputConnection(cc.GetOutputPort())
caster.SetOutputScalarTypeToShort()
caster.ClampOverflowOn()
print('Casting')
caster.Update()

# Writer
writer = vtk.vtkNIFTIImageWriter()
writer.SetFileName(args.outputImage)
writer.SetInputConnection(caster.GetOutputPort())
print("Writing to {}".format(args.outputImage))
writer.Update()
