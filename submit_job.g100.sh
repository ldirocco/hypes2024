#!/bin/bash
#SBATCH --job-name=mpi_example
#SBATCH --ntasks=64          # Number of MPI tasks
#SBATCH --nodes=2           # Number of nodes
#SBATCH --cpus-per-task=1   # Number of cores per MPI task
#SBATCH --output=mpi_output.%j
#SBATCH --time=1:00:00               # time limits: 1 hour
#SBATCH --partition=g100_usr_prod # partition name

# Load necessary modules
module load openmpi
source venv/bin/activate

# Run MPI job
mpirun -np 64 python test_mpi.py
