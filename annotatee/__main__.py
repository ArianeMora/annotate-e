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
import typer
import sys
import pandas as pd
from annotatee import *
from annotatee.annotate import fasta_to_df, pipeline
import os
from typing_extensions import Annotated
from os.path import dirname, join as joinpath

app = typer.Typer()


@app.command()
def fasta(query_fasta: Annotated[str, typer.Argument(help="Full path to query fasta or csv (note have simple IDs otherwise we'll remove all funky characters.)")],
          database: Annotated[str, typer.Argument(help="Full path to database fasta (for BLAST and FoldSeek)")], 
          output_folder: Annotated[str, typer.Option(help="Where to store results (full path!)")] = 'Current Directory', 
          run_name: Annotated[str, typer.Option(help="Name of the run")] = 'annotatee', 
          clean_dir: Annotated[str, typer.Option(help="Directory (full path) to CLEAN - if not using the default)")] = '', 
          proteinfer_dir: Annotated[str, typer.Option(help="Directory (full path) to proteiner - if not using the default)")] = '', 
          run_method: Annotated[str, typer.Option(help="Run method (filter or complete) i.e. filter = only annotates with the next tool those that couldn't be found.")] = 'complete', 
          keep_dups: Annotated[bool, typer.Option(help="Whether or not to keep multiple predicted values if False only the top result is retained.")] = False,
          args_blast: Annotated[str, typer.Option(help="comma separated list (no spaces) of arguments to pass to Diamond BLAST")] = '',
          args_foldseek: Annotated[str, typer.Option(help="comma separated list (no spaces) of arguments to pass to foldseek")] = '',
          args_proteinfer: Annotated[str, typer.Option(help="comma separated list (no spaces) of arguments to pass to ProteInfer")] = '',
          args_clean: Annotated[str, typer.Option(help="comma separated list (no spaces) of arguments to pass to CLEAN")] = '',
          methods: Annotated[str, typer.Option(help="comma separated list (no spaces) of methods to run (e.g. could just pass ['foldseek', 'proteinfer']) to pass to CLEAN")] = '',
          foldseek_db: Annotated[str, typer.Option(help="Database for foldseek to override fasta before (e.g. path to all pdbs as per foldseek docs.)")] = '',
          id_col: Annotated[str, typer.Option(help="id column in df if df passed (csv) rather than fasta")] = 'id',
          seq_col: Annotated[str, typer.Option(help="Database for foldseek to override fasta before (e.g. path to all pdbs as per foldseek docs.)")] = 'seq'):

    """ 
    Find similar proteins based on sequence or structural identity in order to annotate these using 
    BLAST and FoldSeek. Also annotate with ProteInfer and CLEAN.
    """
    pckage_dir = joinpath(dirname(__file__), 'data')
    clean_dir = clean_dir if clean_dir != '' else joinpath(pckage_dir, 'CLEAN/app')
    proteinfer_dir = proteinfer_dir if proteinfer_dir != '' else joinpath(pckage_dir, 'proteinfer')
    # Create a query df from the query fasta
    output_folder = output_folder if output_folder != 'Current Directory' else os.getcwd()
    if '.fa' in query_fasta or '.fasta' in query_fasta and '.csv' not in query_fasta:
        df = fasta_to_df(query_fasta)
    else:
        df = pd.read_csv(query_fasta)
    args_blast = None if args_blast == '' else args_blast.split(',') # type: ignore
    args_foldseek = None if args_foldseek == '' else args_foldseek.split(',') # type: ignore
    args_proteinfer = None if args_proteinfer == '' else args_proteinfer.split(',') # type: ignore
    args_clean = None if args_clean == '' else args_clean.split(',') # type: ignore
    foldseek_db = None if foldseek_db == '' else foldseek_db # type: ignore
    methods = None if methods == '' else methods.split(',') # type: ignore

    # Run the pipeline
    pipeline(run_name, df, id_col, seq_col, output_folder, 
             database, clean_dir=clean_dir, proteinfer_dir=proteinfer_dir,
             run_method=run_method, keep_dups=keep_dups,args_blast=args_blast, args_foldseek=args_foldseek, 
             args_proteinfer=args_proteinfer, args_clean=args_clean, methods=methods, foldseek_db=foldseek_db)


if __name__ == "__main__":
    app()
    
# Example command
#annotatee input_df.csv Uniprot_reviewed_catalytic_activity_06032025.fasta --methods blast --output-folder output/ --run-name omgprot50