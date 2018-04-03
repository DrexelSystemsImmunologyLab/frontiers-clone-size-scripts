import csv
import sys

from collections import Counter
from sqlalchemy import func
from scipy.spatial.distance import cosine
import pandas as pd
import numpy as np

import immunedb.common.config as config
from immunedb.common.models import Clone, CloneStats, Sample, Sequence, Subject


class NoDefaultProvided(object):
    pass


def getattrd(obj, name, default=NoDefaultProvided):
    try:
        return reduce(getattr, name.split('.'), obj)
    except AttributeError, e:
        if default != NoDefaultProvided:
            return default
        raise


def to_dict_dropna(data):
    return dict((k, v.dropna().to_dict())
                for k, v in pd.compat.iteritems(data))


if __name__ == '__main__':
    parser = config.get_base_arg_parser()
    parser.add_argument('subject')
    parser.add_argument('feature')
    parser.add_argument('magnitude',
                        choices=['copies', 'instances'])
    parser.add_argument(
        '--limit-by', choices=['copies', 'instances'], default=None)
    parser.add_argument('--limit-val', type=int, default=None)

    args = parser.parse_args()
    session = config.init_db(args.db_config)

    subject_id = session.query(Subject.id).filter(
        Subject.identifier == args.subject).one().id
    features = {
        s.id: str(getattrd(s, args.feature))
        for s in session.query(Sample).filter(Sample.subject_id == subject_id)
    }
    if args.magnitude == 'instances' or args.limit_by == 'instances':
        instances = session.query(
            Sequence.clone_id,
            Sequence.sample_id,
            func.count(Sequence.seq_id).label('inst')
        ).filter(
            ~Sequence.clone_id.is_(None),
            Sequence.subject_id == subject_id
        ).group_by(
            Sequence.clone_id, Sequence.sample_id
        )
        instances = {(i.clone_id, i.sample_id): i.inst for i in instances}

    clones = session.query(
        Clone.id, Clone.overall_total_cnt, Clone.overall_unique_cnt
    ).filter(Clone.subject_id == subject_id)
    if args.limit_by == 'copies':
        clones = clones.filter(Clone.overall_total_cnt >= args.limit_val)
    elif args.limit_by == 'instances':
        instances_total = Counter()
        for (cid, sid), inst in instances.iteritems():
            instances_total[cid] += inst
        clones = [c for c in clones if instances_total[c.id] >= args.limit_val]
    qualified_clones = set([c.id for c in clones])
    if args.magnitude == 'copies':
        stats = {
            (s.clone_id, s.sample_id): s.total_cnt
            for s in session.query(CloneStats.clone_id, CloneStats.sample_id,
                                   CloneStats.total_cnt).filter(
                    ~CloneStats.sample_id.is_(None))
        }
    elif args.magnitude == 'instances':
        stats = {k: v for k, v in instances.iteritems()}

    clone_rows = {}
    for (clone_id, sample_id), mag in stats.iteritems():
        if clone_id not in qualified_clones:
            continue
        clone_rows.setdefault(
            clone_id, {})[str(features[sample_id])] = float(mag)

    clone_rows = pd.DataFrame.from_dict(clone_rows).transpose().fillna(0)
    header = list(sorted(clone_rows.columns))

    clone_rows = clone_rows.replace(0, np.nan).transpose()
    clone_rows = to_dict_dropna(clone_rows)

    for k, v in clone_rows.iteritems():
        clone_rows[k] = {str(cid): fs for cid, fs in v.iteritems()}
    writer = csv.DictWriter(
        sys.stdout,
        delimiter='\t',
        fieldnames=['feature1', 'feature2', 'similarity']
    )
    writer.writeheader()
    for i in header:
        for j in header:
            if i == j:
                continue
            sim = 1 - cosine(
                [r.get(i, 0) for r in clone_rows.values()],
                [r.get(j, 0) for r in clone_rows.values()]
            )
            writer.writerow({
                'feature1': i,
                'feature2': j,
                'similarity': sim
            })
