for size_i in $(seq 2 4); do
    case $size_i in
        "2") size=copies
            ;;
        "3") size=uniques
            ;;
        "4") size=instances
            ;;
    esac
    echo -e $size
    echo "subject cutoff hill diversity" > diversity_${size}.tsv

    for fn in $@; do
        echo -e "\t" $fn
        for hill in `seq 0 15`; do
            echo -e "\t\thill" $hill
            div=`~/.local/bin/diversity -i $fn -a --std -o - -r $hill -C $size_i -S 1| \
                 awk -F, '{print $6}' | tail -n+2 | head -n 1`
            echo `basename $fn .fasta | awk -F '_' '{print $1" "$2}'` $hill $div >> diversity_${size}.tsv
        done
    done
    sed -i 's/ /\t/g' diversity_${size}.tsv
done
