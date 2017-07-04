# Hisotry:
#   2016.07.18  Michalski   Created
#   2017.03.10  Besler      Edited to remove
#
# Description:
#   Resample QCT image data to be isotropic
#
# Notes:
#   - Based on Michalski's code to perform multiple resamplings
#   - For tabular data printing see http://stackoverflow.com/questions/9535954/printing-lists-as-tabular-data
#   - TODO: Allow user-specified spacing + default to smallest voxel size

## Libraries
import os
import argparse
import vtk

## Establish arguament parser to load the data
parser = argparse.ArgumentParser(
    description='Resample image data to be isotropic',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    'dcmDirectory',
    help='The input DICOM directory')
parser.add_argument(
    'outputFilename',
    help='Output NIfTI-style filename')
parser.add_argument(
    '-f', '--force',
    action='store_true',
    help='Set to overwrite output without asking')
args = parser.parse_args()

## Check our inputs
# Check that the input is a directory
if not os.path.isdir(args.dcmDirectory):
    os.sys.exit('Input \"{dcmDirectory}\" does not exist! Exiting...'.format(dcmDirectory=args.dcmDirectory))

# Check that our output is of type NIfTI
if not args.outputFilename.lower().endswith('.nii'):
    os.sys.exit('Output \"{outputFilename}\" is not of type *.nii! Exiting...'.format(outputFilename=args.outputFilename))

# Make sure we don't overwrite
if os.path.isfile(args.outputFilename):
    if not args.force:
        response = str(raw_input('\"{outputFilename}\" exists. Overwrite? [Y/n]'.format(outputFilename=args.outputFilename)))
        if not 'yes'.startswith(response.lower()):
            os.sys.exit('Exiting to avoid overwrite...')

## Algorithm
# Read input
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName(args.dcmDirectory)
print 'Reading in \"{outputFilename}\"'.format(outputFilename=args.outputFilename)
reader.Update()

# Get voxel information
voxelSize = reader.GetDataSpacing()
targetVoxelSize = float(min(voxelSize))
print 'DICOM spacing: {}'.format(voxelSize)
print 'Target voxel size: {}'.format(targetVoxelSize)

# Resample DICOM to isotropic voxel size
resampler = vtk.vtkImageResample()
resampler.SetInputConnection(reader.GetOutputPort())
resampler.SetInterpolationModeToCubic()
resampler.SetDimensionality(3)
resampler.SetAxisOutputSpacing(0, targetVoxelSize)
resampler.SetAxisOutputSpacing(1, targetVoxelSize)
resampler.SetAxisOutputSpacing(2, targetVoxelSize)
print 'Resampling'
resampler.Update()

# Print information on the input and output
printerMap = {}
printerMap['Dimensions'] = 'GetDimensions'
printerMap['Scalar Type'] = 'GetScalarType'
printerMap['Extent'] = 'GetExtent'
printerMap['Spacing'] = 'GetSpacing'
printerMap['Origin'] = 'GetOrigin'

# This automatically prints a table using the dictionary above.
# This uses a string with a built formatter to develop the table
formatter = "{:>30}" * 3
print formatter.format('', 'Input', 'Output')
for key, value in printerMap.iteritems():
    print formatter.format(
            key,
            eval('reader.GetOutput().{}()'.format(value)),
            eval('resampler.GetOutput().{}()'.format(value)))

# Write data out
writer = vtk.vtkNIFTIImageWriter()
writer.SetInputConnection(resampler.GetOutputPort())
writer.SetFileName(args.outputFilename)
writer.Write()
