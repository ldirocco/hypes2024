import numpy as np
import pandas as pd
import itertools

def read_paf(file_path):
    paf = pd.read_csv(file_path, sep="\t", header=None)[list(range(12))]
    paf.columns = ["q_seq_name", "q_seq_len", "q_start", "q_end", "strand", "t_seq_name", "t_seq_len", "t_start", "t_end", "n_res_match", "align_block_len", "map_quality"]
    return paf



def read_dist_paf(filename, skiprows=0, group_col_idx=0, n_process=1):
    data = []
    with open(filename, 'r') as file:
        # Read the header to use it as column names
        header = ["q_seq_name", "q_seq_len", "q_start", "q_end", 
                  "strand", "t_seq_name", "t_seq_len", "t_start", 
                  "t_end", "n_res_match", "align_block_len", "map_quality"]

        counter = 0
        
        # Iterate over each line in the file
        for line in itertools.islice(file, skiprows, None):
            # Split the line into individual values
            values = line.strip().split('\t')[:12]
            if counter == 0:
                counter += 1
                data = [values]
            else:
                if counter == (n_process + 1):
                    df = pd.DataFrame(data[:-1], columns=header)
                    return df, skiprows + len(df)
                    #data = data[-1:]
                    #counter = 1
                prev_group = data[-1][group_col_idx]
                if values[group_col_idx] == prev_group:
                    data.append(values)
                else:
                    counter += 1
                    data.append(values)
                    
        df = pd.DataFrame(data, columns=header)
        return df, skiprows + len(df)
        