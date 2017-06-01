echo `date +%F\ %H:%M:%S` "START fq2fas" >> ${OUT_FOLDER}.LOG.txt

cd $CLEANING_FOLDER

reads_in=($READS_FILES)

for ((i=0; i<${#reads_in[@]}; i++)); do
    
    tmp=`basename ${reads_in[ i]}`
    mkdir blat_$tmp
     prinseq-lite.pl \
	-fastq ${reads_in[i]} -out_format 1 -out_good blat_${tmp}/reads -out_bad null &

    echo FQ2FAS: IN: ${reads_in[i]} >> ${OUT_FOLDER}.LOG.txt
done
wait
echo `date +%F\ %H:%M:%S` "END fq2fas" >> ${OUT_FOLDER}.LOG.txt

# Options:
# -fastq : the input file is in fastq format
# -out_format 1 : output will be in fasta format
# -out_good : specify the name of the outfile
# -out_bad null : do not produce an out_bad file (not necessary when no filter applied)
