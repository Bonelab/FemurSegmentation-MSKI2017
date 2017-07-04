# History:
#   2017.01.29  babesler    Created
#   2017.03.14  babesler    Moved to only support nii for project
#
# Description:
#   Small script to get a subset of an nii image
#
# Notes:
#   - Ranges are inclusive, so 55->99 starts at index 55 (56th element) and goes
#       untill index 99 (total dimension of 50 elements).
#
# Usage:
#   python QCT_Subget.py input output -l 50 50 50 -u 99 99 99

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
parser.add_argument('-l', '--lower',
                    default=(0,0,0), type=int, nargs=3,
                    help='The lower bound on (x,y,z)')
parser.add_argument('-u', '--upper',
                    default=(-1,-1,-1), type=int, nargs=3,
                    help='The upper bound on (x,y,z)')
parser.add_argument('-s', '--sample',
                    default=(1,1,1), type=int, nargs=3,
                    help='The sample rate on (x,y,z)')
parser.add_argument('-f', '--force',
                    action='store_true',
                    help='Set to overwrite output without asking')
args = parser.parse_args()
lower = list(args.lower)
upper = list(args.upper)

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

# Specify bounds
for i in range(len(lower)):
    # Check that lower is zero or greater
    if lower[i] < 0:
        lower[i] = 0

    # Check that upper is not greater than dimensions
    if upper[i] > dimensions[i] - 1:
        upper[i] = dimensions[i] - 1

    # Make sure bounds are in the correct order
    if upper[i] < lower[i]:
        upper[i], lower[i] = lower[i], upper[i]

print("Using lower bounds {l}".format(l=lower))
print("Using upper bounds {u}".format(u=upper))

# Setup extractor
extractVOI = vtk.vtkExtractVOI()
extractVOI.SetSampleRate(args.sample)
extractVOI.SetVOI(  lower[0], upper[0],
                    lower[1], upper[1],
                    lower[2], upper[2])
extractVOI.SetInputConnection(reader.GetOutputPort())
print("Extracting...")
extractVOI.Update()
print("Extracted VOI has dimensions {dims}".format(dims=extractVOI.GetOutput().GetDimensions()))

# Writer
writer = vtk.vtkNIFTIImageWriter()
writer.SetFileName(args.outputImage)
writer.SetInputConnection(extractVOI.GetOutputPort())
print("Writing to {}".format(args.outputImage))
writer.Update()
