module load PRINSEQ
echo `date +%F\ %H:%M:%S` "START Prinseq triming" >> ${OUT_FOLDER}.LOG.txt
cd $CLEANING_FOLDER

reads_in=($READS_FILES)
reads_out=($READS_OUT)

for ((i=0; i<${#reads_in[@]}; i++)); do

    time srun --exclusive -n1 -c16 -N1 \
	prinseq-lite \
	-fastq ${reads_in[ i ]} \
	-out_good stdout \
	-out_bad null \
	-qual_noscale \
	$PARAM_TRIM \
	-graph_data ${reads_out[ i ]}.stat \
	-graph_stats ld,gc,qd,ns,pt,ts,aq,de,sc,dn \
	-no_qual_header 2> ${STAT_FOLDER}${reads_out[i]}.log.txt \
	> ${reads_out[i]} & 

    echo PRINSEQ_TRIM: IN: ${reads_in[ i ]} OUT: ${reads_out[ i ]} \
	PAR: $PARAM_TRIM >> ${OUT_FOLDER}.LOG.txt
done
wait

PRIN_FOLDER=${OUT_FOLDER}STAT/prinseq_report
if [ ! -d "$PRIN_FOLDER" ]; then
    mkdir $PRIN_FOLDER
fi

for ((i=0; i<${#reads_in[@]}; i++)); do
    # Make the stat graphs:
    prinseq-graphs -i ${reads_out[i]}.stat \
    -o ${OUT_FOLDER}STAT/prinseq_report/${reads_out[ i]}.stat -html_all
    
    rm ${reads_out[i]}.stat
done

echo `date +%F\ %H:%M:%S` "END Prinseq triming" >> ${OUT_FOLDER}.LOG.txt
