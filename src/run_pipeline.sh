#!/bin/bash

# Run this script with following commands
# chmod +x run_pipeline.sh
# ./run_pipeline.sh

# Define arguments
data_dir="../data/"

# file_to_prompt="val-output-employer.jsonl"
file_to_prompt="val-output.jsonl"

# change output directory when rerun to keep the old extractions
output_dir="../extractions/"
# related to the file you use to prompt (ground truth file or test file)
# gold_file="../data/val-output-employer.jsonl"
gold_file="../data/val-output.jsonl"

# modify input data with wikigpt data
# python input-wiki-transformer.py -i "../data/train.jsonl" -o "../data/train-output.jsonl" &
# python input-wiki-transformer.py -i "../data/test.jsonl" -o "../data/test-output.jsonl" &
# python input-wiki-transformer.py -i "../data/val_employer.jsonl" -o "../data/val_employer-output.jsonl" &
# python input-wiki-transformer.py -i "../data/val_profession.jsonl" -o "../data/val_profession-output.jsonl" &
# python input-wiki-transformer.py -i "../data/val_instrument.jsonl" -o "../data/val_instrument-output.jsonl" &
# python input-wiki-transformer.py -i "../data/val_parent_org.jsonl" -o "../data/val_parent_org-output.jsonl" &
python input-wiki-transformer.py -i "../data/val.jsonl" -o "../data/val-output.jsonl" &

# Run the first Python script with arguments in the background
python run.py -d "$data_dir" -f "$file_to_prompt" -o "$output_dir"  -m "gpt-4" &

# Capture the process ID of the first Python script
run_py_pid=$!
echo "process-id: ${run_py_pid}" 

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
