import edlib

def process_target(target, target_sequence, overlapping_df, len_window, fastq_df):
    len_target = len(target_sequence)
    n_windows = len_target // len_window
    if len_target % len_window != 0:
        n_windows += 1
    windows = {}
    for i in range(0, n_windows):
        windows[f"{target}__{i}"]=[target_sequence[(i * len_window): ((i + 1) * len_window)]]
    
    for index, row in overlapping_df.iterrows():
        windows_borders=[]
        r=row['q_start']
        windows_borders=[(0,r//len_window)]
        query_sequence=fastq_df[row['t_seq_name']]
        q_start=row['t_start']
        q_end=row['t_end']
        query_sequence=query_sequence[q_start:q_end]
        edit_distance = edlib.align(query=query_sequence, target=target_sequence, mode="NW", task="path")
        niceNW = edlib.getNiceAlignment(edit_distance, query=query_sequence, target=target_sequence)
        target_alignment=niceNW["target_aligned"]
        query_alignment=niceNW["query_aligned"]
        
        #print(target_alignment)
        #print(query_alignment)
        
        w_id=0
        for i in range(0,len(target_alignment)):
            if target_alignment[i]!='-':
                r+=1
                if r%len_window==0:
                    w_id=r/len_window
                    windows_borders.append((i,w_id))
        w_id+=1
        windows_borders.append((len(query_alignment),w_id))
        #w=windows_borders[0]

        #for i in range(1,len(windows_borders)-1):
        #    w_next=windows_borders[i]
        #    windows[w[1]].append(query_alignment[w[0]:w_next[0]].replace("-",""))
        #    w=w_next
        #windows[w[1]].append(query_alignment[int(len_window*w[1]+1):w[0]].replace("-","")) 
        #print(windows_borders)
    
    return windows


def process_window(key, window):
    # TODO
    graph = {}
    return graph