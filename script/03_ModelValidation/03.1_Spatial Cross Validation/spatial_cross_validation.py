# Spatial Cross Validation
import arcpy
import os
import sys
import numpy as np
import csv

# ------------------------------------------------------------------
# ARGUMENTS
# ------------------------------------------------------------------
# 1: run index
# 2: path to output gdb (existing or to be created)
# 3: metrics folder
# 4: base project folder where DHM etc. live (optional if you use absolute paths)

if len(sys.argv) < 4:
    raise SystemExit("usage: python spatial_cross_validation.py <run_idx> <gdb_path> <metrics_folder>")

run_idx = int(sys.argv[1])
gdb_path = sys.argv[2]
metrics_dir = sys.argv[3]
gdb = r"link_to_a_scratch_gdb" #<-- adjust
metrics = r"link_to_a_metrices_folder" #<-- adjust

# ------------------------------------------------------------------
# DATA
# ------------------------------------------------------------------
base = r"link_to_your_base_folder" #<-- indicate the base folder

# your project gdb:
proj_gdb = os.path.join(base, "Name_of_GDB.gdb") #<-- adjust

in_raster = os.path.join(proj_gdb, "DEM")
in_points = os.path.join(proj_gdb, "presence_points") #<-- adjust
valid_mask = os.path.join(proj_gdb, "mask") #<-- define a mask (highly recommended)
extent_random = os.path.join(proj_gdb, "Extent_for_absence_points") # <-- define a mask for the creation of the absence points

#os.makedirs(metrics_dir, exist_ok=True)

# ------------------------------------------------------------------
# ENVIRONMENT CONFIGURATION
# ------------------------------------------------------------------
arcpy.env.overwriteOutput = True
arcpy.env.addOutputsToMap = False
arcpy.env.processorType = "CPU"
arcpy.env.parallelProcessingFactor = "0"

# create gdb if needed
if not arcpy.Exists(gdb_path):
    folder, gdb_name = os.path.split(gdb_path)
    arcpy.management.CreateFileGDB(folder, gdb_name)

# temp in-memory fcs
rand_points = f"in_memory/rand_{run_idx}"
rand_points_buf = f"in_memory/rand_buf_{run_idx}"
training_fc = f"in_memory/training_{run_idx}"

# ------------------------------------------------------------------
# 1) CREATE RANDOM ABSENCE POINTS
# ------------------------------------------------------------------
tmp_rand_name = f"tmp_rand_{run_idx}"
tmp_rand_full = os.path.join(gdb_path, tmp_rand_name)
if arcpy.Exists(tmp_rand_full):
    arcpy.management.Delete(tmp_rand_full)

arcpy.management.CreateRandomPoints(
    out_path=gdb_path,
    out_name=tmp_rand_name,
    constraining_feature_class=extent_random,
    number_of_points_or_field=415,
    create_multipoint_output="POINT"
)
arcpy.management.CopyFeatures(tmp_rand_full, rand_points)
arcpy.management.Delete(tmp_rand_full)

# 2) buffer (in memory)
arcpy.analysis.PairwiseBuffer(
    in_features=rand_points,
    out_feature_class=rand_points_buf,
    buffer_distance_or_field="50 Meters",
    dissolve_option="NONE",
    method="PLANAR"
)

# 3) merge positives + negatives (in memory)
arcpy.management.Merge(
    inputs=[in_points, rand_points_buf],
    output=training_fc,
    field_match_mode="AUTOMATIC"
)

# 4) label
arcpy.management.CalculateField(
    in_table=training_fc,
    field="Tumulus",
    expression="1 if !OBJECTID! < 415 else 0",
    expression_type="PYTHON3"
)

training_with_block=r"in_memory\training_blocked"

#import sub-areas
sub_area =r"Link_to_Areas_Divided" #<-- adjust 
arcpy.analysis.SpatialJoin(target_features=training_fc, join_features=sub_area, out_feature_class=training_with_block, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")

# ------------------------------------------------------------------
# 5) RUN RANDOM FOREST
# ------------------------------------------------------------------
explanatory_rasters = (
    r"link_to_Crop_Suitability\Crop_Suitability #;" #<-- adjust
    r"link_to_Accessibility\Accessibility #;" #<-- adjust
    r"link_to_Landform_Classification\Landform_Classification true;" #<-- adjust
    r"link_to_Positive-Negative\Positive-Negative #;" #<-- adjust
    r"link_to_Movement\Movement #;" #<-- adjust
    r"link_to_Skyline\Skyline #;" #<-- adjust
    r"link_to_Total_Viewshed\Total_Viewshed #;" #<-- adjust
    r"link_to_Profile_Curvature\Profile_Curvature #;" #<-- adjust
    r"link_to_Slope\Slope #;" #<-- adjust
    r"link_to_Tangential_Curvature\Tangential_Curvature #;" #<-- adjust
    r"link_to_Vegetation\Vegetation true;" #<-- adjust
    r"link_to_Viewshed_Alps\Viewshed_Alps #" #<-- adjust
)
explanatory_rasters_matching = (
    r"link_to_Crop_Suitability\Crop_Suitability Crop_Suitability;" #<-- adjust
    r"link_to_Accessibility\Accessibility Accessibility;" #<-- adjust
    r"link_to_Landform_Classification\Landform_Classification Landform_Classification;" #<-- adjust
    r"link_to_Positive-Negative\Positive-Negative Positive-Negative;" #<-- adjust
    r"link_to_Movement\Movement Movement;" #<-- adjust
    r"link_to_Skyline\Skyline Skyline;" #<-- adjust
    r"link_to_Total_Viewshed\Total_Viewshed Total_Viewshed;" #<-- adjust
    r"link_to_Profile_Curvature\Profile_Curvature Profile_Curvature;" #<-- adjust
    r"link_to_Slope\Slope Slope;" #<-- adjust
    r"link_to_Tangential_Curvature\Tangential_Curvature Tangential_Curvature;" #<-- adjust
    r"link_to_Vegetation\Vegetation Vegetation;" #<-- adjust
    r"link_to_Viewshed_Alps\Viewshed_Alps Viewshed_Alps" #<-- adjust
    )

blocks=sorted({row[0] for row in arcpy.da.SearchCursor(training_with_block,["Id"])})
print("Blocks:",blocks)

metrics =[]
for test_block in blocks:
    train_fc=r"in_memory/train"
    test_fc=r"in_memory/test"
    
    arcpy.analysis.Select(training_with_block,train_fc,f"Id <> {test_block}")
    arcpy.analysis.Select(training_with_block,test_fc,f"Id = {test_block}")
    
    model_output=r"in_memory/model"
    
    with arcpy.EnvManager(
        processorType="CPU",
        parallelProcessingFactor="0",
        snapRaster=in_raster,
        cellSize=in_raster,
        mask=valid_mask,
        extent=valid_mask,
        addOutputsToMap=False):
            
        arcpy.stats.Forest(
            prediction_type="PREDICT_FEATURES",
            in_features=train_fc,
            variable_predict="Tumulus",
            treat_variable_as_categorical="CATEGORICAL",
            explanatory_rasters=explanatory_rasters,
            features_to_predict=test_fc,
            output_features=model_output,
            output_raster=None,
            explanatory_rasters_matching=explanatory_rasters_matching,
            output_trained_features=None, 
            use_raster_values="TRUE",
            number_of_trees=600,
            sample_size=70,
            random_variables=10,
            percentage_for_training=0,
            number_validation_runs=0,
            optimize="FALSE",
            include_probabilities="HIGHEST_PROBABILITY_ONLY",
            model_type="FOREST-BASED")
        if "Tumulus" in [f.name for f in arcpy.ListFields(model_output)]:
            arcpy.DeleteField_management(model_output, ["Tumulus"])
          
        arcpy.management.JoinField(
            in_data=model_output,
            in_field="OBJECTID",        
            join_table=test_fc,
            join_field="OBJECTID",
            fields=["Tumulus"])  
    preds = [row for row in arcpy.da.SearchCursor(model_output,["Tumulus", "PREDICTED"])]
    
    # Compute confusion matrix
    y_true = np.array([p[0] for p in preds])
    y_pred = np.array([p[1] for p in preds])

    tp = np.sum((y_true==1) & (y_pred==1))
    tn = np.sum((y_true==0) & (y_pred==0))
    fp = np.sum((y_true==0) & (y_pred==1))
    fn = np.sum((y_true==1) & (y_pred==0))

    accuracy = (tp+tn)/(tp+tn+fp+fn)
    precision = tp/(tp+fp+1e-9)
    recall = tp/(tp+fn+1e-9)
    F1 = 2*precision*recall/(precision+recall+1e-9)
    mcc = ((tp*tn)-(fp*fn)) / (np.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)) + 1e-9)
    
    metrics.append((test_block, accuracy, precision, recall, F1, mcc))

# ------------------------------------------------------------------
# 6) MODEL METRICS
# ------------------------------------------------------------------

print("Spatial Cross-Validation Metrics:")
for m in metrics:
    print(m)
csv_path = os.path.join(metrics_dir, f"spatial_cv_{run_idx:03}.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["block", "accuracy", "precision", "recall", "F1", "MCC"])
    w.writerows(metrics)
    
print("Saved:",csv_path)

# clean in_memory
arcpy.management.Delete(rand_points)
arcpy.management.Delete(rand_points_buf)
arcpy.management.Delete(train_fc)
arcpy.management.Delete(test_fc)
arcpy.ClearWorkspaceCache_management()
arcpy.management.Delete(training_fc)
arcpy.management.Delete(training_with_block)

print(f"OK run {run_idx}")