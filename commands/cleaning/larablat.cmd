module load BLAT/35INTEL

# IO:
db=`basename $BLAT_READS_DB`

echo `date +%F\ %H:%M:%S` "START blat on reads for database: $db" >> ${OUT_FOLDER}.LOG.txt
#echo -e "Blat on reads custom parameters:\n $PARAM_BLAT" >> ${OUT_FOLDER}.LOG.txt

reads_in=($READS_FILES)

for ((i=0; i<${#reads_in[@]}; i++)); do
    cd $CLEANING_FOLDER
    tmp=`basename ${reads_in[i]}`
    cd blat_$tmp
    mkdir out_blat/$db
    cd queries
    echo BLAT: IN: $tmp DB: $db >> ${OUT_FOLDER}.LOG.txt

    for file in `ls`
    do
	 blat $BLAT_READS_DB $file \
	    $BLAT_TYPE ../out_blat/$db/$file.psl -noHead &

# to add when it will not take ages to run
#$PARAM_BLAT
    done
done
wait

echo `date +%F\ %H:%M:%S` "END blat on reads" >> ${OUT_FOLDER}.LOG.txt
