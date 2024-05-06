import numpy as np
import pandas as pd
from mpi4py import MPI

import subprocess
import edlib
import tqdm 

from src.io import read_fasta, read_fastq, read_maf, read_from_folder, read_paf
from src.utils.lpt import lpt_scheduling
from src.processes import process_target
from src.processes import process_window
from src.utils.split import split_dict_into_chunks


# SETTINGS
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

len_window = 800



## STEP 1: Read data and split target sequence
if rank == 0:
    # Read your DataFrame
    ref_df, fastq_df, maf_df = read_from_folder("data")
    #minimap = subprocess.call("src/utils/minimap.sh", shell=True)
    paf_df = read_paf("data/overlap.paf")

    # Split DataFrame into jobs
    schedule = []
    overlapping_dfs = {}
    for target, overlapping_df in paf_df.groupby("q_seq_name"):
        schedule.append((target, len(overlapping_df)))
        overlapping_dfs[target] = overlapping_df
        
    schedule = lpt_scheduling(schedule, size - 1)
    for i in range(1, size):
        jobs = []
        for target, _ in schedule[i-1]:
            target_sequence = fastq_df[target]
            jobs.append((target, target_sequence, overlapping_dfs[target],len_window, fastq_df))
        # Send jobs to other processes
        comm.send(jobs, dest=i)

else:
    # Receive chunk from master process
    data_jobs = comm.recv(source=0)
    
    # Perform parallel processing on received chunk
    processed = {}
    for data_job in data_jobs:
        processed.update(process_target(*data_job))

    # Send back the processed chunk
    comm.send(processed, dest=0)


## STEP 2: split windows and generate graphs
if rank == 0:
    # Receive processed chunks from other processes and concatenate them
    windows = {}
    for i in range(1, size):
        processed = comm.recv(source=i)
        windows.update(processed)

    # Final windows
    print("num windows:", len(windows))
    jobs = split_dict_into_chunks(windows, size - 1)
    for i in range(1, size):
        comm.send(jobs[i-1], dest=i)

else:
    # Receive chunk from master process
    data_jobs = comm.recv(source=0)
    #print(data_jobs)
    processed = {}
    for k, w in data_jobs.items():
        processed.update(process_window(k, w))
    # Send back the processed chunk
    comm.send(processed, dest=0)
   

## STEP 3: All graphs into dict!
if rank == 0:
    # Receive processed chunks from other processes and concatenate them
    graphs = {}
    for i in range(1, size):
        processed = comm.recv(source=i)
        graphs.update(processed)

    print("graphs:", graphs)
    
        
    
    

    
