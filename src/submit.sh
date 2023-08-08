#!/bin/bash
#
#SBATCH --job-name=test-gpt
#SBATCH --output=prompting.txt
#
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18
#SBATCH --gpus=1
#SBATCH -p gpu
#SBATCH -t 02:00:00

srun hostname
source activate kgc
python run.py -d ../data/ -o ../extractions/ -l

