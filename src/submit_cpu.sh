#!/bin/bash
#Set job requirements
#SBATCH --job-name=kbc
#SBATCH --output=prompting.txt
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=staging
#SBATCH --time=02:00:00

srun python run.py -d dataset2023/data/ -o extractions/ -l
