from itertools import islice

def split_dict_into_chunks(dictionary, num_chunks):
    dict_items = list(dictionary.items())
    chunk_size = len(dict_items) // num_chunks
    return [dict(dict_items[i:i+chunk_size]) for i in range(0, len(dict_items), chunk_size)]
