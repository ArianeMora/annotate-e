import os
from multiprocessing.dummy import Pool as ThreadPool

def run(cmd):
    os.system(cmd)

runs = []
count = 0
files = os.listdir('data/')
for f in files:
    if f != 'train-00001-of-00032' and f!= 'train-00027-of-00032' and f != 'train-00003-of-00032' and f != 'train-00004-of-00032' and f != 'train-00009-of-00032' and f != 'train-00013-of-00032' and f != 'train-00019-of-00032' and f != 'train-00022-of-00032' and f != 'train-00023-of-00032' and f != 'train-00026-of-00032' and f != 'train-00028-of-00032':
        #cmd = f'annotatee fasta /disk1/ariane/vscode/annotate-e/experiments/degradeo/data/{f}/input_df.csv /disk1/ariane/vscode/annotate-e/experiments/degradeo/Uniprot_reviewed_catalytic_activity_06032025.fasta --methods blast,foldseek  --foldseek-db /disk1/share/software/foldseek/structures/pdb/pdb --output-folder /disk1/ariane/vscode/annotate-e/experiments/degradeo/output/ --run-name omgprot50_{f}'
        cmd = f'annotatee fasta /disk1/ariane/vscode/annotate-e/experiments/degradeo/data/{f}/input_df.csv /disk1/ariane/vscode/annotate-e/experiments/degradeo/Uniprot_reviewed_catalytic_activity_06032025.fasta --methods blast --output-folder /disk1/ariane/vscode/annotate-e/experiments/degradeo/output/ --run-name omgprot50_{f}'
        os.system(cmd)
        #break
        #runs.append(cmd)
        #count += 1
        #if count == 2:
        #    break
# num_threads = 2
# pool = ThreadPool(num_threads)
# output_filenames = pool.map(run, runs)