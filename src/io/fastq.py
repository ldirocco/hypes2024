import numpy as np
import pandas as pd

def read_fastq(file_path):
    """
    Import FASTQ file and return a list of sequences.

    Args:
    - file_path (str): Path to the FASTQ file.

    Returns:
    - pandas DataFrame: DataFrame containing sequence id, sequence, and quality scores.
    """
    sequences = {}
    with open(file_path, "r") as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            if lines[i][0] == "@":
                seq_id = lines[i].strip()[1:]
                sequence = lines[i+1].strip()
                #quality = lines[i+3].strip()
                sequences[seq_id] = sequence #, quality))
                i += 4
            else:
                i += 1
    #columns = ['seq_id', 'sequence', 'quality']
    #sequences = pd.DataFrame(sequences, columns=columns)
    return sequences