set -e

echo "Making FASTA files"
python make_fasta.py $DB_CONFIG --min-instances $(seq 1 10)
echo "Running rarefaction"
bash run_rf.sh *.fasta
echo "Running diversity"
bash run_diversity.sh *.fasta
