set -e
subject=$1
python calculate.py $DB_CONFIG $subject --min-instances $(seq 1 20) > ${subject}_metrics.tsv
