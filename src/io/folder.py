import numpy as np
import pandas as pd
import glob

from .fasta import read_fasta
from .fastq import read_fastq
from .maf import read_maf


def read_from_folder(folder_path):
    ref_files = glob.glob(f"{folder_path}/*.ref")
    fastq_files = glob.glob(f"{folder_path}/*.fastq")
    maf_files = glob.glob(f"{folder_path}/*.maf")

    ref_df = pd.concat([read_fasta(file) for file in ref_files])
    #fastq_df = pd.concat([read_fastq(file) for file in fastq_files])
    fastq_df = {}
    for d in [read_fastq(file) for file in fastq_files]:
        fastq_df.update(d)
    maf_df = pd.concat([read_maf(file) for file in maf_files])
    return ref_df, fastq_df, maf_df