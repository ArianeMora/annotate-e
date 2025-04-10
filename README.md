# annotate-e

Annotator for enzymes using an ensemble of tools to annoatte function to genes.

![overview](images/searching.png)


## Install:

``` 
pip install annotatee
```

### Depending on which/if all tools install each respective tool
``` 
source install_scripts/diamond.sh
source install_scripts/foldseek.sh
source install_scripts/clean.sh
source install_scripts/proteinfer.sh
```
You'll need to pass the directory of the install for CLEAN and proteInfer to `annotatee`. e.g. `--clean-dir ...../CLEAN/app/`

Note! requires enzymetk to also be installed: [enzymetk](https://github.com/ArianeMora/enzyme-tk). 
```
pip install enzymetk
```

## Run:

## Setup:
Download sequences for your database or use ours. 
e.g. the fasta file from UniProt SwissProt with annotations.

Note you'll also need to setup [proteinfer](https://github.com/google-research/proteinfer)  
[CLEAN](https://github.com/tttianhao/CLEAN). I'm working on uploading their data automatically - lmk if you need these or have troubles installing them.

## Arguments:
Pass a fasta file as the database and a fasta file that you seek to search against the database. 

The database will first get searched for existing anontations, and otherwise ML methods will be used.

Example command:
```
annotatee input_df.csv Uniprot_reviewed_catalytic_activity_06032025.fasta --methods blast --output-folder output/ --run-name omgprot50
```

### Help

```
annotattee --help

 Usage: annotatee [OPTIONS] QUERY_FASTA DATABASE                                                                                                                                                       
                                                                                                                                                                                                       
 Find similar proteins based on sequence or structural identity in order to annotate these using  BLAST and FoldSeek. Also annotate with ProteInfer and CLEAN.                                         
                                                                                                                                                                                                       
╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    query_fasta      TEXT  Full path to query fasta or csv (note have simple IDs otherwise we'll remove all funky characters.) [default: None] [required]                                          │
│ *    database         TEXT  Full path to database fasta (for BLAST and FoldSeek) [default: None] [required]                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output-folder                           TEXT  Where to store results (full path!) [default: Current Directory]                                                                                    │
│ --run-name                                TEXT  Name of the run [default: annotatee]                                                                                                                │
│ --clean-dir                               TEXT  Directory (full path) to CLEAN - if not using the default)                                                                                          │
│ --proteinfer-dir                          TEXT  Directory (full path) to proteiner - if not using the default)                                                                                      │
│ --run-method                              TEXT  Run method (filter or complete) i.e. filter = only annotates with the next tool those that couldn't be found. [default: complete]                   │
│ --keep-dups             --no-keep-dups          Whether or not to keep multiple predicted values if False only the top result is retained. [default: no-keep-dups]                                  │
│ --args-blast                              TEXT  comma separated list (no spaces) of arguments to pass to Diamond BLAST                                                                              │
│ --args-foldseek                           TEXT  comma separated list (no spaces) of arguments to pass to foldseek                                                                                   │
│ --args-proteinfer                         TEXT  comma separated list (no spaces) of arguments to pass to ProteInfer                                                                                 │
│ --args-clean                              TEXT  comma separated list (no spaces) of arguments to pass to CLEAN                                                                                      │
│ --methods                                 TEXT  comma separated list (no spaces) of methods to run (e.g. could just pass ['foldseek', 'proteinfer']) to pass to CLEAN                               │
│ --foldseek-db                             TEXT  Database for foldseek to override fasta before (e.g. path to all pdbs as per foldseek docs.)                                                        │
│ --id-col                                  TEXT  id column in df if df passed (csv) rather than fasta [default: id]                                                                                  │
│ --seq-col                                 TEXT  Database for foldseek to override fasta before (e.g. path to all pdbs as per foldseek docs.) [default: seq]                                         │
│ --install-completion                            Install completion for the current shell.                                                                                                           │
│ --show-completion                               Show completion for the current shell, to copy it or customize the installation.                                                                    │
│ --help                                          Show this message and exit.                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```