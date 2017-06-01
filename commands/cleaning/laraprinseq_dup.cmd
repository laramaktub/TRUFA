
echo `date +%F\ %H:%M:%S` "START Prinseq only dup" >> ${OUT_FOLDER}.LOG.txt
cd $CLEANING_FOLDER

reads_in=($READS_FILES)

reads_out=($READS_OUT)


if [ ${#reads_in[@]} -eq 2 ]; then

	prinseq-lite.pl \
	-fastq ${reads_in[0]} \
	-fastq2 ${reads_in[1]} \
	-derep 1 \
	-derep_min 2 \
	-out_good good \
	-out_bad null \
	-qual_noscale \
	-no_qual_header \
	2> ${STAT_FOLDER}prinseq_paired_duplication.log.txt
    wait
# To keep the correct output names (cannot pass by stdin)
    mv good_1.fastq ${reads_out[0]}
    mv good_2.fastq ${reads_out[1]}

    echo PRINSEQ_DUP: IN: ${reads_in[@]} OUT: ${reads_out[@]} \
	PAR: $PARAM_DUP >> ${OUT_FOLDER}.LOG.txt


elif [ ${#reads_in[@]} -eq 1 ]; then 

    
	prinseq-lite.pl \
	-fastq ${reads_in[0]} \
	-out_good stdout \
	-out_bad null \
	-qual_noscale \
	$PARAM_DUP \
	-no_qual_header 2> ${STAT_FOLDER}${reads_out[0]}_dup.log.txt \
	> ${reads_out[0]} & 

    echo PRINSEQ_DUP: IN: ${reads_in[0]} OUT: ${reads_out[0]} \
	PAR: $PARAM_DUP >> ${OUT_FOLDER}.LOG.txt
else 
    echo "Neither 1 or 2 reads files. Check prinseq_dup.cmd"
fi
wait
echo `date +%F\ %H:%M:%S` "END Prinseq only dup" >> ${OUT_FOLDER}.LOG.txt

# NO GRAPHS anymore >>> caused crashes
#	-graph_data dup/stat \
#	-graph_stats ld,gc,qd,ns,pt,ts,aq,de,sc,dn \
