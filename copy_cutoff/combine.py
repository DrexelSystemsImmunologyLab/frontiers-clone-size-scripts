import pandas as pd
import glob

dfs = {
    fn: pd.read_csv(fn, sep='\t', index_col='copies')
    for fn in glob.glob('copy_cutoff_*.tsv')
}
for fn, df in dfs.iteritems():
    df.columns = [fn.rsplit('_', 1)[1].replace('.tsv', '')]
pd.concat(dfs.values(), axis=1).to_csv('copy_cutoff.tsv', sep='\t')
