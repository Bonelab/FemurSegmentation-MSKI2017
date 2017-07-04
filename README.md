# FemurSegmentation-MSKI2017
Scripts used for the conference proceeding "B.A. Besler, A.S. Michalski, N.D. Forkert, S.K. Boyd. “Automatic Full Femur Segmentation from Computed Tomography Datasets using an Atlas-Based Approach”. Computational Methods and Clinical Applications in Musculoskeletal Imaging: 5th International Workshop and Challenge, MSKI 2017, Held in Conjunction with MICCAI 2017. Quebec City, September 10th–14th, 2017."

# Project Structure
```bash
.
├── COM
│   ├── helperScripts
│   └── imageProc
└── DOC
```

`COM` contains scripts used for this project. VTK 7 and simpleitk should be used for executing those scripts.
`helperScripts` contains scripts used for verification and checking.
`imageProc` contains scripts which did some image processing, such as thresholding or dilation. This also contains the Elastix files.

# Krcah Segmentation
The Kcrcah segmentation technique is [available online](https://github.com/mkrcah/bone-segmentation).
This project also contains some excellent datasets for testing against.
I was only able to build the project against ITK v3.10.2.
This can be checked out as a tag from the online [git repository](https://github.com/InsightSoftwareConsortium/ITK).
When building ITK, enable flags `-std=c++0x –fpermissive` and include `ITK_REVIEW`.

# Elastix
Elastix version 4.8 was used for thie project.
It can be attained from the [Elastix Website](http://elastix.isi.uu.nl/).
For the selection criterion, first run the `Affine.txt` file with your data
Metrics can be grabbed using grep (`grep -r -a "Final Metric: " *`).
Sort the metrics by hand and run the best ranked metric with the `BSpline.txt` file.
