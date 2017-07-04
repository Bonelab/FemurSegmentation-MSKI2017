# History:
#   2017.04.11  babesler    Created
#
# Description:
#   Compute metrics of overlap between two images
#
# Notes:
#   - See the following links for a description of the metrics:
#       https://itk.org/Doxygen/html/classitk_1_1LabelOverlapMeasuresImageFilter.html
#       https://itk.org/Doxygen/html/classitk_1_1HausdorffDistanceImageFilter.html
#
# Usage:
#   python QCT_Metrics.py input output

import vtk
import argparse
import os
import SimpleITK as sitk

# Setup and parse command line arguments
parser = argparse.ArgumentParser(description='Extract whole body mask',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('inputImage1',
                    help='The first input NIfTI (*.nii) image)')
parser.add_argument('inputImage2',
                    help='The second input NIfTI (*.nii) image)')
parser.add_argument('-o', '--outputFile',
                    default=None,
                    help='The output text file, defaults to standard out if nothing given')
parser.add_argument('-d', '--delimiter',
                    default=',', type=str,
                    help='The output text file, defaults to standard out if nothing given')
parser.add_argument('-n', '--nThreads',
                    default=1, type=int,
                    help='Number of threads')
args = parser.parse_args()

# Constants for formatting the output string
template='{InputFile1}{del}{InputFile2}{del}{HausdorffDistance}{del}{FalseNegativeError}{del}{FalsePositiveError}{del}{VolumeSimilarity}{del}{JaccardCoefficient}{del}{DiceCoefficient}{del}{MeanOverlap}{del}{UnionOverlap}\n'.replace('{del}', args.delimiter)
header=template.replace('{','').replace('}','') # Notice that we can remove string formatting and auto-generate header!

# Check that input file exists
for fileName in [args.inputImage1, args.inputImage2]:
    if not fileName.lower().endswith('.nii'):
        os.sys.exit('Output file \"{outputImage}\" is not a .nii file. Exiting...'.format(outputImage=fileName))

    if not os.path.isfile(fileName):
        os.sys.exit('Input file \"{inputImage}\" does not exist. Exiting...'.format(inputImage=fileName))

# Check that the number of threads is valid
if args.nThreads < 1:
    os.sys.exit('Must have atleast one threads, asked for {}. Exiting...'.format(args.nThreads))

# Create the file writer
if args.outputFile is None:
    writer = os.sys.stdout
    writer.write(header)
else:
    # See if the file exists already. If not, write header
    if os.path.isfile(args.outputFile):
        try:
            writer = open(args.outputFile, 'a')
        except IOError:
            os.sys.exit('Unable to open file {} for appending. Exiting...'.format(args.outputFile))
    else:
        try:
            writer = open(args.outputFile, 'w')
            writer.write(header)
        except IOError:
            os.sys.exit('Unable to open file {} for writing. Exiting...'.format(args.outputFile))

# Read the inputs
inputImage1 = sitk.ReadImage(args.inputImage1)
inputImage2 = sitk.ReadImage(args.inputImage2)

# Compute HausdorffDistance
hdFilter = sitk.HausdorffDistanceImageFilter()
hdFilter.SetNumberOfThreads(args.nThreads)
print('Computing Hausdorff Distance with {} threads'.format(args.nThreads))
hdFilter.Execute(inputImage1, inputImage2)

# Compute everything else
overlapFilter = sitk.LabelOverlapMeasuresImageFilter()
overlapFilter.SetNumberOfThreads(args.nThreads)
print('Computing other Overlap Measures with {} threads'.format(args.nThreads))
overlapFilter.Execute(inputImage1, inputImage2)

result = template.format(
    InputFile1=args.inputImage1,
    InputFile2=args.inputImage2,
    HausdorffDistance=hdFilter.GetHausdorffDistance(),
    FalseNegativeError=overlapFilter.GetFalseNegativeError(),
    FalsePositiveError=overlapFilter.GetFalsePositiveError(),
    VolumeSimilarity=overlapFilter.GetVolumeSimilarity(),
    JaccardCoefficient=overlapFilter.GetJaccardCoefficient(),
    DiceCoefficient=overlapFilter.GetDiceCoefficient(),
    MeanOverlap=overlapFilter.GetMeanOverlap(),
    UnionOverlap=overlapFilter.GetUnionOverlap()
)

# Write results
writer.write(result)

# Clean up
if writer is not os.sys.stdout:
    writer.close()
