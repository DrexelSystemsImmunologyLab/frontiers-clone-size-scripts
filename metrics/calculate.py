import numpy as np
import pandas as pd

from sqlalchemy.orm import joinedload

import immunedb.common.config as config
from immunedb.common.models import Clone, Subject

if __name__ == '__main__':
    parser = config.get_base_arg_parser()
    parser.add_argument('subject')
    parser.add_argument('--min-instances', nargs='+', type=int, default=[1])
    args = parser.parse_args()

    session = config.init_db(args.db_config)

    subject_id = session.query(Subject.id).filter(
        Subject.identifier == args.subject).one().id

    metrics = []
    for min_instances in args.min_instances:
        instance_metrics = {}
        clones = session.query(
            Clone.overall_total_cnt,
            Clone.overall_instance_cnt,
            Clone.overall_unique_cnt
        ).filter(
            Clone.subject_id == subject_id
        )
        if min_instances > 1:
            clones = clones.filter(
                Clone.overall_instance_cnt >= min_instances)
        for metric in ('total', 'instance', 'unique'):
            proportions = [
                getattr(c, 'overall_{}_cnt'.format(metric)) for c in clones
            ]
            total = float(sum(proportions))
            proportions = [p/total for p in proportions]
            shannon_diversity = -sum([p * np.log(p) for p in proportions])
            simpson_index = sum([p ** 2 for p in proportions])

            pielous_evenness = shannon_diversity / np.log(len(proportions))
            instance_metrics[metric] = {
                'shannon_diversity': shannon_diversity,
                'pielous_evenness': pielous_evenness,
                'richness': len(proportions),
                'simpson_index': simpson_index,
                'clonality': 1.0 / simpson_index,
            }
        metrics.append(pd.DataFrame.from_dict(instance_metrics,
                                              orient='index'))
    df = pd.concat(metrics, keys=args.min_instances)
    df.index = df.index.rename(['min_instances', 'metric'])
    print df.to_csv(sep='\t')
