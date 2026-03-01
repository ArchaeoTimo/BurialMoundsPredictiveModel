# Raster-based Model.py
import arcpy
import os
import sys

# ------------------------------------------------------------------
# ARGUMENTS
# ------------------------------------------------------------------
# 1: run index
# 2: path to output gdb (existing or to be created)
# 3: metrics folder
# 4: base project folder where DHM etc. live (optional if you use absolute paths)

if len(sys.argv) < 4:
    raise SystemExit("usage: python raster-based_model.py <run_idx> <gdb_path> <metrics_folder>")

run_idx       = int(sys.argv[1])
gdb_path      = sys.argv[2]
metrics_dir   = sys.argv[3]

# ------------------------------------------------------------------
# DATA
# ------------------------------------------------------------------
base = r"link_to_your_base_folder" #<-- indicate the base folder

# project gdb:
proj_gdb = os.path.join(base, "Name_of_GDB.gdb") #<-- adjust

in_raster     = os.path.join(proj_gdb, "DEM")
in_points     = os.path.join(proj_gdb, "presence_points") #<-- adjust
valid_mask    = os.path.join(proj_gdb, "mask") #<-- define a mask (highly recommended)
extent_random = os.path.join(proj_gdb, "Extent_for_absence_points") # <-- define a mask for the creation of the absence points

os.makedirs(metrics_dir, exist_ok=True)

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

# names for this run
prediction_raster = os.path.join(gdb_path, f"prediction_prob_{run_idx:03}")
imp_table_tmp = os.path.join(gdb_path, f"var_imp_{run_idx:03}")
cls_table_tmp = os.path.join(gdb_path, f"class_{run_idx:03}")

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

with arcpy.EnvManager(
    processorType="CPU",
    parallelProcessingFactor="0",
    snapRaster=in_raster,
    cellSize=in_raster,
    mask=valid_mask,
    extent=valid_mask,
    addOutputsToMap=False
):
    arcpy.stats.Forest(
        prediction_type="PREDICT_RASTER",
        in_features=training_fc,
        variable_predict="Tumulus",
        treat_variable_as_categorical="CATEGORICAL",
        explanatory_rasters=explanatory_rasters,
        explanatory_rasters_matching=explanatory_rasters_matching,
        output_raster=prediction_raster,
        output_trained_features=None,               
        output_importance_table=imp_table_tmp,      
        output_classification_table=cls_table_tmp, 
        use_raster_values="TRUE",
        number_of_trees=600,
        sample_size=70,
        random_variables=10,
        percentage_for_training=45,
        number_validation_runs=5,
        optimize="FALSE",
        include_probabilities="ALL_PROBABILITIES",
        model_type="FOREST-BASED"
    )

# ------------------------------------------------------------------
# 6) MODEL METRICS
# ------------------------------------------------------------------
imp_csv = os.path.join(metrics_dir, f"var_imp_prob_{run_idx:03}.csv")
cls_csv = os.path.join(metrics_dir, f"class_prob_{run_idx:03}.csv")

arcpy.conversion.TableToTable(imp_table_tmp, metrics_dir, os.path.basename(imp_csv))
arcpy.conversion.TableToTable(cls_table_tmp, metrics_dir, os.path.basename(cls_csv))

arcpy.management.Delete(imp_table_tmp)
arcpy.management.Delete(cls_table_tmp)

# clean in_memory
arcpy.management.Delete(rand_points)
arcpy.management.Delete(rand_points_buf)
arcpy.management.Delete(training_fc)
arcpy.ClearWorkspaceCache_management()

print(f"OK run {run_idx}")
