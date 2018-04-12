#!/usr/bin/env python2
import sys
from sqlalchemy.orm import joinedload
from sqlalchemy import func

import immunedb.common.config as config
from immunedb.common.models import Clone, CloneStats, Sequence


if __name__ == '__main__':
    parser = config.get_base_arg_parser()
    parser.add_argument('--min-instances', type=int, default=[1],
                        nargs='+')
    args = parser.parse_args()

    session = config.init_db(args.db_config)

    print 'Gathering clone statistics'
    stats = session.query(
        CloneStats
    ).options(
        joinedload(CloneStats.sample),
    ).filter(
        ~CloneStats.sample_id.is_(None)
    )

    print 'Calculating instances'
    sample_instances = {
        (s.clone_id, s.sample_id): s.inst for s in session.query(
        Sequence.clone_id,
        Sequence.sample_id,
        func.count(Sequence.seq_id).label('inst')
    ).filter(
        ~Sequence.clone_id.is_(None)
    ).group_by(
        Sequence.clone_id, Sequence.sample_id
    )}

    instances = {s.clone_id: s.inst for s in session.query(
        Sequence.clone_id,
        Sequence.sample_id,
        func.count(Sequence.seq_id).label('inst')
    ).filter(
        ~Sequence.clone_id.is_(None)
    ).group_by(
        Sequence.clone_id
    )}

    print 'Writing files'
    for min_instances in args.min_instances:
        fhs = {}
        counted_uniques = set()
        for stat in stats:
            identifier = stat.sample.subject.identifier
            clone_instances = instances.get(stat.clone_id, 0)
            if clone_instances < min_instances:
                continue

            if identifier not in fhs:
                fhs[identifier] = open(
                    '{}_C{}.fasta'.format(identifier, min_instances), 'w+'
                )
            fh = fhs[identifier]

            if stat.clone_id in counted_uniques:
                uniques = 0
            else:
                uniques = stat.unique_cnt
            counted_uniques.add(stat.clone_id)
            sizes = '|'.join((str(s) for s in (
                stat.total_cnt,
                uniques,
                sample_instances.get((stat.clone_id, stat.sample_id))
            )))
            fh.write('>{}|{}\n{}\n'.format(
                stat.sample.name,
                sizes,
                stat.clone_id
            ))
        [fh.close() for fh in fhs.values()]
