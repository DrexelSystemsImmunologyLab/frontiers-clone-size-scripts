import csv
import sys

from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import joinedload

import immunedb.common.config as config
from immunedb.common.models import Clone, Subject


if __name__ == '__main__':
    parser = config.get_base_arg_parser()
    parser.add_argument('--min-instances', type=int, default=None)
    args = parser.parse_args()
    session = config.init_db(args.db_config)

    clones = session.query(
        Clone,
        func.count(Clone.id).label('count'),
        func.sum(Clone.overall_unique_cnt).label('uniques'),
        func.sum(Clone.overall_instance_cnt).label('instances'),
        func.sum(Clone.overall_total_cnt).label('copies'),
    ).options(
        joinedload(Clone.subject)
    ).group_by(
        Clone.subject_id,
        Clone.v_gene
    )
    if args.min_instances:
        clones = clones.filter(Clone.overall_instance_cnt >=
                               args.min_instances)

    writer = csv.DictWriter(sys.stdout, delimiter='\t', fieldnames=[
        'subject', 'v_gene', 'clones', 'clones_uniques', 'clones_instances',
        'clones_copies'
    ])
    writer.writeheader()
    for clone in clones:
        writer.writerow({
            'subject': clone.Clone.subject.identifier,
            'v_gene': clone.Clone.v_gene,
            'clones': clone.count,
            'clones_uniques': clone.uniques,
            'clones_instances': clone.instances,
            'clones_copies': clone.copies
        })
