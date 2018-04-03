set -e

cat size.sql | immunedb_sql $DB_CONFIG --query - > sizes.tsv
python clone_size.py
