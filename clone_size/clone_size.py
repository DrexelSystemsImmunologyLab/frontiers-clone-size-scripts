import pandas as pd


def rank_subject_clones(df, subject, by, limit=20):
    df = df[df.identifier == subject]
    df = df.drop(['identifier'], axis=1)
    norm_df = df / df.sum()
    norm_df = norm_df.sort_values(by, ascending=False).reset_index()
    return norm_df[:limit]


if __name__ == '__main__':
    df = pd.read_csv('sizes.tsv', delimiter='\t', index_col='id')
    for subject in df.identifier.unique():
        for by in ('overall_unique_cnt', 'instance_cnt', 'overall_total_cnt'):
            pdf = rank_subject_clones(df, subject, by)
            pdf = pdf.to_csv('{}_ranks_by_{}.tsv'.format(subject, by),
                             sep='\t')
