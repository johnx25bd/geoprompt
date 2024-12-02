#!/bin/bash

# Define the bounding box and output directory
BBOX="-0.146821,51.521142,-0.052669,51.583499"
OUTPUT_DIR="data"
FORMAT="geojson"

# Create the output directory if it doesn't exist
# mkdir -p $OUTPUT_DIR

# List of types to download
TYPES=("address" "building" "building_part" "division" "division_area" "division_boundary" "place" "segment" "connector" "infrastructure" "land" "land_cover" "land_use" "water")

# Loop through each type and download the data
for TYPE in "${TYPES[@]}"; do
  echo "Downloading data for type: $TYPE"
  overturemaps download --bbox=$BBOX -f $FORMAT --type=$TYPE -o $OUTPUT_DIR/islington-$TYPE.json
  if [ $? -ne 0 ]; then
    echo "Failed to download data for type: $TYPE"
  else
    echo "Downloaded data for type: $TYPE"
  fi
done

echo "Download complete."
