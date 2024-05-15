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
/g100_work/PROJECTS/spack/v0.17/prod/0.17.1/install/0.17/linux-centos8-cascadelake/gcc-10.2.0/openmpi-4.1.1-xcbaflrhirzvtiy3y5cnglgyfunavtx3/bin/mpirun -np 64 python test_mpi.py
