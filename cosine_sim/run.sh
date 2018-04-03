set -e

subject=$1
sim () {
    local i=$1
    local subject=$2
    echo $i $subject
    python similarity.py $DB_CONFIG $subject id copies \
        --limit-by instances --limit-val $i > similarity_C${i}_copies.tsv
    python similarity.py $DB_CONFIG $subject id instances \
        --limit-by instances --limit-val $i > similarity_C${i}_instances.tsv
}

for i in $(seq 1 5); do
    sim $i $subject
done
