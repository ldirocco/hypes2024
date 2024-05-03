import numpy as np
import pandas as pd

def read_maf(file_path, ref_file=True):
    """
    Import custom MAF file and return a pandas DataFrame.

    Args:
    - file_path (str): Path to the MAF file.

    Returns:
    - pandas DataFrame: DataFrame containing MAF data.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    maf_data = [x.replace("\n", "").replace("s", "").split() for x in lines if (x != 'a\n') and (x != '\n')]
    maf_data = [maf_data[i] + maf_data[i+1] for i in range(0, len(maf_data), 2)]
    columns = ['ref_seq_id', 'ref_start', 'ref_lenght', 'A', 'B', 'ref_seq_alignment', 'seq_id', 'start', 'lenght', 'C', 'D', 'seq_alignment']
    maf_data = pd.DataFrame(maf_data, columns=columns)

    if ref_file:
        with open(file_path.replace(".maf", ".ref"), 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('>'):
                    sequence_id = line[1:]
                    break
        maf_data["ref_seq_id"] = sequence_id
    return maf_data