import numpy as np
import pandas as pd

def read_fasta(file_path):
    sequences = {'ref_seq_id': [], 'sequence': []}

    with open(file_path, 'r') as file:
        sequence_id = None
        sequence = ''
        for line in file:
            line = line.strip()
            if line.startswith('>'):
                # If there was a previous sequence, save it
                if sequence_id:
                    sequences['ref_seq_id'].append(sequence_id)
                    sequences['sequence'].append(sequence)
                # Start a new sequence
                sequence_id = line[1:]
                sequence = ''
            else:
                sequence += line

        # Add the last sequence
        if sequence_id:
            sequences['ref_seq_id'].append(sequence_id)
            sequences['sequence'].append(sequence)

    df = pd.DataFrame(sequences)
    return df