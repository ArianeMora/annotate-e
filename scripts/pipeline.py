from sciutil import SciUtil
import os
import pandas as pd
from enzymetk.sequence_search_blast import BLAST
from enzymetk.similarity_foldseek_step import FoldSeek
from enzymetk.annotateEC_proteinfer_step import ProteInfer
from enzymetk.annotateEC_CLEAN_step import CLEAN
from enzymetk.save_step import Save
import pandas as pd
from tqdm import tqdm
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool


u = SciUtil()

def pipeline(run_name, input_df, id_col, seq_col, output_folder):
    try:
        input_df << (BLAST(id_col, seq_col, database='../data/uniprot_sprot_enzymes.fasta', args=['--ultra-sensitive']) >> Save(os.path.join(output_folder, f'{run_name}_blast.pkl')))

        # After this we summarize the BLAST file
        df = pd.read_pickle(os.path.join(output_folder, f'{run_name}_blast.pkl'))
        df.sort_values(by='sequence identity', ascending=False, inplace=True)
        df = df.drop_duplicates(subset=['query'])
        # Now we would check which ones were unable to be found
        # existing seqs
        df['annotation'] = 'BLAST'
        # Override with the smaller df
        df.to_pickle(os.path.join(output_folder, f'{run_name}_blast.pkl'))
        
        input_df = input_df[~input_df[id_col].isin(df['query'])]
        # Save this as the one to run with foldseek
        input_df.to_pickle(os.path.join(output_folder, f'{run_name}_torun_foldseek.pkl'))
        u.dp([len(df), 'identified by BLAST. Continuing with ', len(input_df)])
    except Exception as e:
        u.dp([f'Error with BLAST: {e}'])
        u.dp([f'Continuing with FoldSeek'])

    # try:
    #     # Now we need to do foldseek against these remaining sequences
    #     reference_database = '/disk1/share/software/foldseek/structures/pdb/pdb'
    #     if len(input_df) > 0:
    #         input_df << (FoldSeek(id_col, seq_col, reference_database, query_type='seqs') >> Save(os.path.join(output_folder, f'{run_name}_foldseek.pkl')))
    #         min_fident = 0.1
    #         foldseek_df = pd.read_pickle(os.path.join(output_folder, f'{run_name}_foldseek.pkl'))
    #         foldseek_df.sort_values(by='fident', ascending=False, inplace=True)
    #         foldseek_df = foldseek_df.drop_duplicates(subset=['query'])
    #         foldseek_df = foldseek_df[foldseek_df['fident'] > min_fident]
    #         # Now we would check which ones were unable to be found
    #         # existing seqs
    #         foldseek_df['annotation'] = 'foldseek'
    #         input_df = input_df[~input_df[id_col].isin(foldseek_df['query'])]
    #         # Override with the smaller df
    #         foldseek_df.to_pickle(os.path.join(output_folder, f'{run_name}_foldseek.pkl'))
    #         # Now we need to do foldseek against these remaining sequences
    #         u.dp([len(foldseek_df), 'identified by FoldSEEK. Continuing with ', len(input_df)])
    # except Exception as e:
    #     u.dp([f'Error with FoldSeek: {e}'])
    #     u.dp([f'Continuing with ProteInfer'])

    # # Running proteInfer 
    # try:    
    #     if len(input_df) > 0:
    #         input_df << (ProteInfer(id_col, seq_col, proteinfer_dir='/disk1/ariane/vscode/enzyme-tk/enzymetk/conda_envs/proteinfer/') >> Save(os.path.join(output_folder, f'{run_name}_proteinfer.pkl')))

    #         proteinfer_df = pd.read_pickle(os.path.join(output_folder, f'{run_name}_proteinfer.pkl'))
    #         min_fident = 0.5
    #         proteinfer_df.sort_values(by='confidence', ascending=False, inplace=True)
    #         proteinfer_df = proteinfer_df.drop_duplicates(subset=['sequence_name'])
    #         proteinfer_df = proteinfer_df[proteinfer_df['confidence'] > min_fident]
    #         # Now we would check which ones were unable to be found
    #         # existing seqs
    #         proteinfer_df['annotation'] = 'proteinfer'
    #         # Continue with all sequences since we are unsure with ML
    #         #input_df = input_df[~input_df['id'].isin(proteinfer_df['sequence_name'])]
    #         u.dp([len(proteinfer_df), 'identified by ProteInfer. Continuing with ', len(input_df)])
    #         # Override with the smaller df
    #         proteinfer_df.to_pickle(os.path.join(output_folder, f'{run_name}_proteinfer.pkl'))
    # except Exception as e:
    #     u.dp([f'Error with ProteInfer: {e}'])
    #     u.dp([f'Continuing with CLEAN'])

    # # CLEAN directory
    # try:   
    #     if len(input_df) > 0:
    #         clean_dir = '/disk1/share/software/CLEAN/app/'
    #         input_df << (CLEAN(id_col, seq_col, clean_dir, num_threads=1) >> Save(os.path.join(output_folder, f'{run_name}_clean.pkl')))
    # except Exception as e:
    #     u.dp([f'Error with CLEAN: {e}'])

def __execute(data):
    run_name, input_df, output_folder = data[0], data[1], data[2]
    pipeline(run_name, input_df, id_col, seq_col, output_folder)
    return run_name

id_col = 'id'
label_col = 'label'
seq_col = 'sequence'    
num_threads = 50

def execute(df: pd.DataFrame, output_folder: str) -> pd.DataFrame:
    # Have a max size of 1000 * nthreads 
    first_chunksize = len(df)/(num_threads * 1000)
    
    df_chunks = np.array_split(df, first_chunksize)
    cj = 0
    for df in tqdm(df_chunks):
        if num_threads > 1:
            data = []
            df_list = np.array_split(df, num_threads)
            pool = ThreadPool(num_threads)
            ri = 0
            for df_chunk in tqdm(df_list):
                #__execute([f'r{ri}', df_chunk])
                data.append([f'c{cj}r{ri}', df_chunk, output_folder])
                ri += 1
            results = pool.map(__execute, data)
            cj += 1
            u.dp(['DONE', len(df_list), len(results)])

#og_df = pd.read_parquet('/disk1/share/data/OG/data/train-00000-of-00110.parquet')
files = os.listdir('/disk1/share/data/OMG_prot50/data/')
for f in files:
    print(f)
    og_df = pd.read_parquet(f'/disk1/share/data/OMG_prot50/data/{f}')
    # Sample the dataframe into parts
    # Then we want to convert the IDs and the sequneces
    j = 0

    id_col = 'id'
    label_col = 'label'
    seq_col = 'seq'  
    output_folder = f'/disk1/ariane/vscode/annotate-e/data/OMG_prot50/{f.replace(".parquet", "")}/'
    print(output_folder)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
        rows = []
        # I think chunking is better since we don't need to do this 
        for s_id, seqs in tqdm(og_df[['id', 'sequence']].values): #og_df[['CDS_ids', 'CDS_seqs']].values):
            rows.append([f'o{j}', s_id, seqs])
            #for i, s_id in enumerate(ids):
            #    rows.append([f'o{j}s{i}', s_id, seqs[i]])
            j += 1
        input_df = pd.DataFrame(rows, columns=['id', 'cds_id', 'seq'])
        # Save first 
        input_df.to_pickle(f'{output_folder}input_df.pkl')
        # Save the input df to a file as well since then we can extract this as well 
        execute(input_df, output_folder)