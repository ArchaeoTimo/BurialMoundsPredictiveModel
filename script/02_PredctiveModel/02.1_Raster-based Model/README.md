# Predictive Model

This folder contains the scripts required to reproduce the machine-learning–based predictive modelling framework described in the paper.

The modelling approach combines Monte Carlo simulation of absence sampling with a raster-based Random Forest classifier implemented in ArcGIS Pro.

## Overview
The predictive workflow consists of repeated independent model runs.
Each run:
- Generates random absence points.
- Merges absence and presence data into a training dataset.
- Trains a Random Forest model.
- Produces a raster-based probability surface.
- Exports model metrics (variable importance and classification table).

The script raster-based_model.py performs a single model run. Multiple runs are executed iteratively via PowerShell to obtain aggregated probability surfaces.

## Required Input Data
All required datasets must exist in the project geodatabase:
- DEM
- presence_points
- mask (*modelling extent*)
- Extent_for_absence_points (*Polygon constraining random absence generation*)

In addition, all explanatory rasters must be available and correctly linked in the script:
- Crop Suitability
- Accessibility
- Landform Classification
- Positive–Negative
- Movement
- Skyline
- Total Viewshed
- Profile Curvature
- Slope
- Tangential Curvature
- Vegetation
- Viewshed Alps

Paths to these rasters must be adjusted in the script prior to execution.

### Reproducibility Notes
- Absence points are generated randomly for each run.
- Random Forest training involves stochastic elements. Therefore, results will vary slightly between runs.
- Aggregated results across multiple runs are used to stabilise model outputs.
- Due to site protection legislation, burial mound coordinates cannot be published. To reproduce the workflow, dummy presence data must be generated.
- The DEM and modelling mask are provided in the repository. Presence points and the extent polygon for absence generation cannot be shared due to site protection legislation. 

## How to run
All datasets that need further specification are marked with "# <-- adjust" in the python script.

The script is executed from PowerShell using the *PowerShell_Prompt_rasterbased_model* prompt. The location of the python script needs to be specified in the PowerShell prompt.
