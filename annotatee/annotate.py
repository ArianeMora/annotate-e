###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

"""
Author: Ariane Mora
Date: September 2024
"""
# Use chai to fold the structure
from Bio import SeqIO
import pandas as pd
import re

import sys
sys.path.append('/disk1/ariane/vscode/enzyme-tk/')
import os
from enzymetk.sequence_search_blast import BLAST
from enzymetk.similarity_foldseek_step import FoldSeek
from enzymetk.annotateEC_proteinfer_step import ProteInfer
from enzymetk.annotateEC_CLEAN_step import CLEAN
from sciutil import SciUtil
import subprocess
import timeit
import logging
import subprocess

u = SciUtil()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
u = SciUtil()


def fasta_to_df(fasta):
    rows = []
    records = list(SeqIO.parse(fasta, "fasta"))
    done_records = []
    # Remove all the ids
    for record in records:
        new_id = re.sub('[^0-9a-zA-Z]+', '', record.id)
        if new_id not in done_records:
            rows.append([new_id, record.seq])
        else:
            u.warn_p(['Had a duplicate record! Only keeping the first entry, duplicate ID:', record.id])
    df = pd.DataFrame(rows, columns=['id', 'seq'])
    return df


def run(cmd: list) -> None:
    """ Run a command """
    start = timeit.default_timer()
    u.dp(['Running command', ' '.join([str(c) for c in cmd])])
    result = subprocess.run(cmd, capture_output=True, text=True)       
    u.warn_p(['Output:'])
    print(result.stdout)
    u.err_p(['Error:', result.stderr])
    if result.stderr:
        logger.error(result.stderr)
    logger.info(result.stdout)
    u.dp(['Time for command to run (min): ', (timeit.default_timer() - start)/60])
        
        
def run_blast(run_name, input_df, id_col, seq_col, output_folder, database, run_method, keep_dups,
             args_blast=None, num_threads=1):
    """ 
    Annotate sequences using BLAST.
    """
    blast_df = (input_df << (BLAST(id_col, seq_col, database=database, args=args_blast)))
    # After this we summarize the BLAST file
    blast_df.sort_values(by='sequence identity', ascending=False, inplace=True)
    if not keep_dups:
        blast_df = blast_df.drop_duplicates(subset=['query'])
    # Now we would check which ones were unable to be found
    blast_df['annotation'] = 'BLAST'
    # Override with the smaller df
    blast_df.to_csv(os.path.join(output_folder, f'{run_name}_blast.csv'), index=False)
    if run_method == 'filter':
        input_df = input_df[~input_df[id_col].isin(blast_df['query'])]
    # Also add in the annotations to the dataframe
    u.dp([len(blast_df), 'identified by BLAST. Continuing with ', len(input_df)])
    return input_df

    
def run_proteinfer(run_name, input_df, id_col, seq_col, output_folder, run_method, proteinfer_dir, keep_dups=False, args_proteinfer=None):
    proteinfer_df = (input_df << (ProteInfer(id_col, seq_col, proteinfer_dir=proteinfer_dir)))
    proteinfer_df.sort_values(by='confidence', ascending=False, inplace=True)
    # Check if they want to retain the duplicate IDs
    if not keep_dups:
        proteinfer_df = proteinfer_df.drop_duplicates(subset=['sequence_name'])
    # Now we would check which ones were unable to be found existing seqs
    proteinfer_df['annotation'] = 'proteinfer'
    # Continue with all sequences since we are unsure with ML
    if run_method == 'filter':
        input_df = input_df[~input_df['id'].isin(proteinfer_df['sequence_name'])]
        
    u.dp([len(proteinfer_df), 'identified by ProteInfer. Continuing with ', len(input_df)])
    # Override with the smaller df
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Change it back just incase the user isn't in the right directory or passed a relative path
    os.chdir(dir_path)
    proteinfer_df.to_csv(os.path.join(output_folder, f'{run_name}_proteinfer.csv'), index=False)
    return input_df


def run_foldseek(run_name: str, input_df: pd.DataFrame, id_col: str, seq_col: str, output_folder: str, 
                 database: str, run_method: str, keep_dups, args_foldseek=None) -> pd.DataFrame:
    # Now we need to do foldseek against these remaining sequences
    # Check if the reference database is a fasta, if so make the reference db in the output folder
    try:
        subprocess.check_output('nvidia-smi')
        gpu = 1
    except Exception: # this command not being found can raise quite a few different errors depending on the configuration
        gpu = 0
    if os.path.isfile(database) and '.fa' in database:
        # Make the DB using foldseek
        u.warn_p(['Making the foldseek database, WARNING: this may take some resources...', f'db_{run_name}'])
        db_path = os.path.join(output_folder, 'foldseek_db')
        try:
            os.mkdir(db_path)
        except:
            u.warn_p(['Warning: you already had a foldseek db path in the output folder...'])
        os.chdir(db_path)
        cmd = ['foldseek', 'databases', 'ProstT5', 'weights', 'tmp']
        run(cmd)
        # Make the db first 
        cmd = ['foldseek', 'createdb', database, f'db_{run_name}', '--prostt5-model', 'weights', '--gpu', str(gpu)]
        run(cmd)
        database = os.path.join(db_path, f'db_{run_name}')
    # Run foldseek
    foldseek_df = (input_df << (FoldSeek(id_col, seq_col, database, query_type='seqs', args=args_foldseek)))
    foldseek_df.sort_values(by='fident', ascending=False, inplace=True)
    # Change back 
    if not keep_dups:
        foldseek_df = foldseek_df.drop_duplicates(subset=['query'])
    # Now we would check which ones were unable to be found
    foldseek_df['annotation'] = 'foldseek'
    # Override with the smaller df
    foldseek_df.to_csv(os.path.join(output_folder, f'{run_name}_foldseek.csv'), index=False)
    # Now we need to do foldseek against these remaining sequences
    u.dp([len(foldseek_df), 'identified by FoldSEEK. Continuing with ', len(input_df)])
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Change it back just incase the user isn't in the right directory or passed a relative path
    os.chdir(dir_path)
    # Check if we filter or just run each tool on each dataset
    if run_method == 'filter':
        input_df = input_df[~input_df[id_col].isin(foldseek_df['query'].values)]
    
    return input_df
    
def run_clean(run_name: str, input_df: pd.DataFrame, id_col: str, seq_col: str, output_folder: str, clean_dir: str, keep_dups: bool, 
              args_clean=None) -> pd.DataFrame:
    clean_df = (input_df << (CLEAN(id_col, seq_col, clean_dir, num_threads=1)))
    rows = []
    for values in clean_df.values:
        values = values[0]
        values = values.split(',')
        for ec in values[1:]:
            ec = ec.split('/')
            rows.append([values[0].split('seq')[0], ec[0], ec[1]])
    clean_df = pd.DataFrame(rows, columns=['id', 'EC', 'value'])
    clean_df.sort_values(by='value', ascending=True, inplace=True)

    if not keep_dups:
        clean_df = clean_df.drop_duplicates(subset=['id'])
        
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Change it back just incase the user isn't in the right directory or passed a relative path
    os.chdir(dir_path)
    clean_df.to_csv(os.path.join(output_folder, f'{run_name}_clean.csv'), index=False)

    return input_df    

def pipeline(run_name: str, input_df: pd.DataFrame, id_col: str, seq_col: str, output_folder: str, database: str, 
             clean_dir: str, proteinfer_dir: str, run_method='complete', keep_dups=False, args_blast=None, 
             args_foldseek=None, args_proteinfer=None, args_clean=None, 
             methods=None, foldseek_db=None):
    """ 
    By default run all methods but otherwise select only those based on the 
    """
    # Need to change the ids to not have any funny characters
    u.warn_p(['Removing any special characters from your IDs as this will cause issues with CLEAN.'])
    u.warn_p(['Dropping any duplicate labels.'])
    input_df[id_col] = [re.sub('[^0-9a-zA-Z]+', '', s) for s in input_df[id_col].values]
    input_df = input_df.drop_duplicates(subset=id_col)
    # Do the same for the fasta file to make sure they still match
    u.warn_p(['Removing funky characters from fasta ids as well. Saving to:', os.path.join(output_folder, f'{run_name}_input_fasta.fasta')])
    with open(os.path.join(output_folder, f'{run_name}_input_fasta.fasta'), 'w+') as fout:
        records = list(SeqIO.parse(database, "fasta"))
        done_records = []
        # Remove all the ids
        for record in records:
            new_id = re.sub('[^0-9a-zA-Z]+', '', record.id)
            if new_id not in done_records:
                fout.write(f">{new_id}\n{record.seq}\n")
            else:
                u.warn_p(['Had a duplicate record! Only keeping the first entry, duplicate ID:', record.id])
    # Reset db
    database = os.path.join(output_folder, f'{run_name}_input_fasta.fasta')
    if not methods or 'blast' in methods:
        try:
            if not args_blast:
                args_blast = ['--ultra-sensitive']
            run_blast(run_name, input_df, id_col, seq_col, output_folder, database, run_method, keep_dups, args_blast)
        except Exception as e:
            u.dp([f'Error with BLAST: {e}'])
            u.dp([f'Continuing with FoldSeek'])
    if not methods or 'foldseek' in methods:
        try:
            if not args_foldseek:
                args_foldseek = ['--cov-mode', '2']
            # Now we need to do foldseek against these remaining sequences
            if len(input_df) > 0:
                if foldseek_db is None: # optionally pass a precomputed DB for this
                    foldseek_db = database
                input_df = run_foldseek(run_name, input_df, id_col, seq_col, output_folder, foldseek_db, run_method, keep_dups, args_foldseek)
        except Exception as e:
            u.dp([f'Error with FoldSeek: {e}'])
            u.dp([f'Continuing with ProteInfer'])

    # Running proteInfer 
    if not methods or 'proteinfer' in methods:
        try:    
            if len(input_df) > 0:
                # def run_proteinfer(run_name, input_df, id_col, seq_col, output_folder, run_method, keep_dups=False, args_proteinfer=None):

                input_df = run_proteinfer(run_name, input_df, id_col, seq_col, output_folder, run_method, proteinfer_dir, 
                                          keep_dups, args_proteinfer=args_proteinfer)
        except Exception as e:
            u.dp([f'Error with ProteInfer: {e}'])
            u.dp([f'Continuing with CLEAN'])

    # CLEAN 
    if not methods or 'clean' in methods:
        try:   
            if len(input_df) > 0:
                input_df = run_clean(run_name, input_df, id_col, seq_col, output_folder, clean_dir, keep_dups=keep_dups, args_clean=args_clean)
        except Exception as e:
            u.dp([f'Error with CLEAN: {e}'])
        