set -e

for fn in $@; do
    echo "Running rarefaction for $fn"
    ~/.local/bin/diversity --whole-sequence -S 1 -i $fn -o \
        temp.csv -d --sample -c temp -C 2 -I "1 1 19"
    awk -F',' '{print $6"\t"$7}' temp > `basename $fn .fasta`.tsv
    rm temp
    rm temp.csv
done
