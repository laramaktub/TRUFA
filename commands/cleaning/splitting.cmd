module load PYTHON

echo `date +%F\ %H:%M:%S` "START splitting" >> ${OUT_FOLDER}.LOG.txt

reads_in=($READS_FILES)

for ((i=0; i<${#reads_in[@]}; i++)); do

    cd $CLEANING_FOLDER
    tmp=`basename ${reads_in[ i]}`
    cd blat_$tmp
    mkdir out_blat
    mkdir queries

    time srun --exclusive -n1 -c4 -N1 ${PY_BIOLIB_PATH}fasta_split4blat.py reads.fasta queries/reads.splitted 32 &
    echo SPLITTING: IN: ${reads_in[ i ]} >> ${OUT_FOLDER}.LOG.txt
done
wait

echo `date +%F\ %H:%M:%S` "END splitting" >> ${OUT_FOLDER}.LOG.txt
