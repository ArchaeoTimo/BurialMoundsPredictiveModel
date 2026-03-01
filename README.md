# README

This repository contains code and data necessary to reproduce the modelling workflow of the paper:

**Their Final Resting Place:**  
*A machine-learning-based predictive model approach towards the geospatial location of burial mounds in western Switzerland*

Timo Geitlinger  
*Institute for Archaeology, Philology, and Ancient Studies, University of Zurich, Zurich, Switzerland*

This paper presents a framework for a machine-learning-based predictive model approach for burial mound site locations in western Switzerland. By combining multiple machine-learning techniques with iterative Monte Carlo simulations and a diverse set of covariates approximating past human experience, the empirical basis and robustness of the model are substantially enhanced. The workflow provides a transferable framework for (predictive) modelling in other archaeological contexts.

## Structure of the repository
The repository folder is structured as follows:

- **README.md:** Repository overview and usage instructions.

- **script/**: Python scripts for covariate preparation, predictive modelling, and model validation.
  - *01_Covariates/*: Scripts for covariate generation.
    - 01.1_Hydrology
    - 01.2_Skyline
    - 01.3_Accessibility
    - 01.4_Movement
  - *02_PredictiveModel/*
    - 02.1_Raster-based Model
    - 02.2_Point-based Model
  - *03_ModelValidation/*
    - 03.1_Spatial Cross Validation
- **data/**: Data used for covariate generation, modelling, validation, and exploration.
  - *00_Site information/*
    - 00.1_Burial Mounds: Inventory of alls burial mounds (no coordinates provided)
    - 00.2_Detected Features: Results from the Automatic Detection Machine Learning Model
  - *01_Covariate/*: Data to reproduce the model results:
    - 01.1_Hydrology
    - 01.2_Skyline
    - 01.3_Accessibility
    - 01.4_Movement
    - 01.5_Crop suitability
    - 01.6_Total visibility
    - 01.7_Visibility Alps
  - *02_PredictiveModel/*
    - 02.1_Raster-based Model
    - 02.2_Points-based Model
  - *03_ModelValidation/*
    - 03_1_Spatial Cross Validation
  - *04_ModelExploration/*
    - 04_1_Bias Assessment
- **SupplementaryInformation.pdf**

## Scripts:
Each script in this repository has a brief caption explaining its function and how to implement it in arcpy. The scripts were run using arcpy from **ArcGIS pro (Version 3.6.0)** on Windows 11. Each modelling step includes:
- A geodatabse containing required input data
- A Python notebook or script
- Supplementary configuration files

### Required Extentions
The workflow requires:
- Spatial Analyst
- 3D Analyst
- ArcGIS Pro (valid license)

### ***WARNINGS***

Due to site protection legislation, the dataset containing burial mound coordinates cannot be published. To execute scripts in 02_PredictiveModel and 03_ModelValidation, users must generate dummy burial site data.

The analyses are computationally demanding. Insufficient memory or processing capacity may result in slow performance or system instability. The original analyses were conducted on a system with 32 GB RAM, and individual modelling steps required multiple days of computation.

Some modelling components rely on stochastic Monte Carlo simulation. Results may therefore vary slightly between runs.
### How to run the script

#### 01 Covariates:
1. Open the corresponding Notebook in ArcGIS Pro.
2. Add all required dataset to the current Map.
3. Review input paths and parameters in the script header.
4. Execute each cell sequentially

#### 02 Predictive Model and 03 Spatial Cross Validation:
Due to computational demands, these scripts were executed iteratively via PowerShell.
1. Open PowerShell
2. Adjust file paths in powershell_command.txt.
3. Execute the command.
A valid ArcGIS Pro license is required.

## Data
The data directory is organized by modelling stage:
- 00 – Data compilation
- 01 – Covariate generation
- 02 – Predictive modelling
- 03 – Cross validation
- 04 – Model exploration

Data formats include:
- File Geodatabase rasters
- File Geodatabase feature classes
- Shapefiles (.shp)
- CSV files (.csv)
- Text files (.txt)
  
The coordinate reference system is generally **LV95 / CH 1903+ (EPSG:2056)**.

## Computational Environment
All analyses and code development were conducted on:

Windows 11 (64-bit): OMEN X by HP Laptop  
ArcGIS Pro (Version 3.6.0) using the Spatial Analyst and 3D Analyst extension
