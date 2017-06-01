

echo `date +%F\ %H:%M:%S` "START FastQC" >> ${OUT_FOLDER}.LOG.txt

reads_in=($READS_FILES)

for ((i=0; i<${#reads_in[@]}; i++)); do

    fastqc -t 2  --noextract ${reads_in[ i ]} -o ${STAT_FOLDER}fastqc_report
    echo FASTQC: IN: ${reads_in[ i ]} >> ${OUT_FOLDER}.LOG.txt
done
wait

echo `date +%F\ %H:%M:%S` "END FastQC" >> ${OUT_FOLDER}.LOG.txt

