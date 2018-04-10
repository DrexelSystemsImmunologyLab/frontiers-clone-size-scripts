import csv
import json
import sys

from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import joinedload

import immunedb.common.config as config
from immunedb.common.models import CloneStats


def get_muts(clone):
    muts = json.loads(clone.mutations).get('regions', {})
    counts = Counter()
    for region_muts in muts.values():
        for mut_type, type_muts in region_muts.iteritems():
            key = 'replacement' if 'conservative' in mut_type else mut_type
            counts.update({key: m['total'] for m in type_muts})
    counts['total'] = sum(counts.values())
    return counts


if __name__ == '__main__':
    parser = config.get_base_arg_parser()
    args = parser.parse_args()
    session = config.init_db(args.db_config)

    clones = session.query(
        CloneStats,
    ).options(joinedload(CloneStats.clone)).filter(
        CloneStats.sample_id.is_(None)
    )

    writer = csv.DictWriter(sys.stdout, delimiter='\t', fieldnames=[
        'clone_id', 'size', 'subject', 'synonymous', 'replacement', 'total',
    ], extrasaction='ignore')
    writer.writeheader()
    for clone in clones:
        row = {
            'clone_id': clone.id,
            'subject': clone.clone.subject.identifier,
            'size': clone.clone.overall_total_cnt
        }
        row.update(get_muts(clone))
        writer.writerow(row)
