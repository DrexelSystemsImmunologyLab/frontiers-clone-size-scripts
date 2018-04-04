subs=`immunedb_sql $DB_CONFIG --query 'select identifier from subjects' --no-head`

for subject in $subs
do
    sid=`immunedb_sql $DB_CONFIG --no-head --query \
        "select id from subjects where identifier='${subject}'"`
    immunedb_sql $DB_CONFIG --query "
        select (count(*) / (select count(*) from clones where subject_id=$sid)) as fraction,
               overall_total_cnt as copies
        from clones
        where subject_id=$sid
        group by overall_total_cnt
        order by count(*) desc" > copy_cutoff_${subject}.tsv
done
