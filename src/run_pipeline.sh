#!/bin/bash

# Run this script with following commands
# chmod +x run_pipeline.sh
# ./run_pipeline.sh

# Define arguments
data_dir="../data/"
file_to_prompt="random_val_sample2-output.jsonl"

# change output directory when rerun to keep the old extractions
output_dir="../extractions_random_100/"
# related to the file you use to prompt (ground truth file or test file)
gold_file="../data/random_val_sample2-output.jsonl"

# Run the first Python script with arguments in the background
python run.py -d "$data_dir" -f "$file_to_prompt" -o "$output_dir" &

# Capture the process ID of the first Python script
run_py_pid=$!

# Wait for the first Python script to finish
wait "$run_py_pid"

# Run the second Python script after the first one has finished
# The location of the result_parser.py might differ
extraction_file="${output_dir}extractions.jsonl"
python ../result_parser.py -p "$extraction_file" -g "$gold_file" -o "$output_dir"

# Wait for result_parser.py to finish before running evaluate.py
wait
prediction_file="${output_dir}prediction-for-eval.jsonl"
# Run the third Python script after result_parser.py has finished
python ../evaluate.py -p "$prediction_file" -g "$gold_file"
# Wait for evaluate.py to finish before exiting the script
wait
