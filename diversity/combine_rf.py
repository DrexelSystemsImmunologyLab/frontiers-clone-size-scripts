import argparse
import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    parser.add_argument('--suffix', default='')
    args = parser.parse_args()

    dfs = {fn: pd.read_csv(fn, sep='\t', index_col='subsample')
           for fn in args.files}
    df = pd.concat(dfs, axis=1)
    df.columns = df.columns.droplevel(-1)
    df.to_csv('rf{}.tsv'.format(
        '_' + args.suffix if args.suffix else ''), sep='\t')
