#!/bin/bash
#Set job requirements
#SBATCH --job-name=kbc
#SBATCH --output=prompting.txt
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --partition=defq
#SBATCH --time=1-00:00:00

module load cuda11.7/toolkit
srun python3 run.py
