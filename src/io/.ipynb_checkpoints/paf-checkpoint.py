import numpy as np
import pandas as pd


def read_paf(file_path):
    paf = pd.read_csv(file_path, sep="\t", header=None)[list(range(12))]
    paf.columns = ["q_seq_name", "q_seq_len", "q_start", "q_end", "strand", "t_seq_name", "t_seq_len", "t_start", "t_end", "n_res_match", "align_block_len", "map_quality"]
    return paf