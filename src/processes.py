import edlib
import pyabpoa as pa

def process_target(target, t_seq, overlapping_df, len_window, fastq_df):
    l=len(t_seq)
    overlapping_df=paf_df[paf_df["q_seq_name"] == target]
    n_windows=l//wLength
    if l%wLength!=0:
        n_windows+=1
    windows={}
    prev_index=0
    for i in range(0,n_windows):
        windows[i]=[t_seq[prev_index:min((i+1)*wLength,l)]]
        prev_index=min((i+1)*wLength,l)
    
    for index, row in overlapping_df.iterrows():
        windows_borders=[]
        t_start=row['q_start']
        t_end=row['q_end']
        q_start=row['t_start']
        q_end=row['t_end']
        windows_borders=[(-1,t_start//wLength)]
        query_sequence=fastq_df[fastq_df['seq_id']==row['t_seq_name']]['sequence'].iloc[0]
        query_sequence=query_sequence[q_start:q_end+1]
        target_sequence=t_seq[t_start:t_end+1]
        edit_distance = edlib.align(query=query_sequence, target=target_sequence, mode="NW", task="path")
        niceNW = edlib.getNiceAlignment(edit_distance, query=query_sequence, target=target_sequence)
        target_alignment=niceNW['target_aligned']
        query_alignment=niceNW['query_aligned']
        w_id=0
        for i in range(0,len(target_alignment)):
            if target_alignment[i]!='-':
                t_start+=1
                if t_start%wLength==0:
                    w_id=t_start/wLength
                    windows_borders.append((i,w_id))
        w_id+=1
        windows_borders.append((len(query_alignment),w_id))
        w=windows_borders[0]
        for i in range(1,len(windows_borders)):
            if w[1]>=n_windows:
                    break
             w_next=windows_borders[i]
    
    return windows


def process_window(key, window):
    consensus_sequence=''
    for i in range(0,len(windows)):
        w_consensus=a.msa(windows[i], out_cons=True, out_msa=True)
        consensus_sequence+=w_consensus.cons_seq[0]
    
    return consensus_sequence
