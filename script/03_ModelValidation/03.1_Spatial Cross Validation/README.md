# Spatial Cross Validation

This folder contains the script required to reproduce the spatial block cross-validation procedure described in the paper.

The spatial cross-validation framework evaluates model performance under spatial partitioning to account for spatial autocorrelation and to assess generalisation performance across independent sub-regions.

## Overview
The predictive workflow consists of repeated independent model runs.
Each run:
- Generates random absence points.
- Merges absence and presence data into a training dataset.
- Assigns all samples to spatial blocks (*sub-areas*).
- Iteratively withholds one block as test data.
- Trains a Random Forest model on the remaining blocks.
- Predicts class labels for the withheld block.
- Computes performance metrics manually.

The script *spatial_cross_validation.py* performs a single model run. Multiple runs are executed iteratively via PowerShell to obtain aggregated probability surfaces.

## Method:
For each block, a model is trained on all remaining blocks and evaluated on the withheld block.

Reported metrics include:
- Accuracy
- Precision
- Recall
- F1-score
- Matthews Correlation Coefficient (MCC)

## Required Input Data
All required datasets must exist in the project geodatabase:
- DEM
- presence_points
- mask (*modelling extent*)
- Extent_for_absence_points (*Polygon constraining random absence generation*)
- Spatial block layer (*pre-defined sub-areas*)

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

### Reproducibility Notes
- Absence points are generated randomly for each run.
- Random Forest training involves stochastic elements. Therefore, results will vary slightly between runs.
- Aggregated results across multiple runs are used to stabilise model outputs.
- Due to site protection legislation, burial mound coordinates cannot be published. To reproduce the workflow, dummy presence data must be generated.
- The DEM and modelling mask are provided in the repository. Presence points and the extent polygon for absence generation cannot be shared due to site protection legislation. 

## How to run
All datasets that need further specification are marked with "# <-- adjust" in the python script.

The script is executed from PowerShell using the *PowerShell_Prompt_pointbased_model* prompt. The location of the python script needs to be specified in the PowerShell prompt.
