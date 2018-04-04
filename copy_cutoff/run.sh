subs=`immunedb_sql $DB_CONFIG --query 'select identifier from subjects' --no-head`

for subject in $subs
do
    immunedb_sql $DB_CONFIG --query \
        "select (count(*) / (select count(*) from clones)) as count, overall_total_cnt as copies
        from clones
        where subject_id=(select id from subjects where identifier='${subject}')
        group by overall_total_cnt order by count(*) desc" \
            > copy_cutoff_${subject}.tsv
done
