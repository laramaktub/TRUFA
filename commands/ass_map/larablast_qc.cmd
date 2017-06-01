echo `date +%F\ %H:%M:%S` "START BLAST_ASSEMBLY_QC" >> ${OUT_FOLDER}.LOG.txt

cd $ASSEMBLY_MAPPING_FOLDER

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE

else
    echo "EK: check the blast_qc code"
fi

#### Blast check (as suggested by Trinity team)

time blastx \
    -query $transcripts -db $BLAST_QUAL_DB \
    -out ${STAT_FOLDER}assembly_qc/blast_qc/blastx.outfmt6 \
    -evalue 1e-20 -num_threads 16 \
    -max_target_seqs 1 -outfmt 6

time /software/applications/trinityrnaseq/v2.2.0/util/analyze_blastPlus_topHit_coverage.pl ${STAT_FOLDER}assembly_qc/blast_qc/blastx.outfmt6 $transcripts $BLAST_QUAL_DB

#### Basic statistics:

${PY_BIOLIB_PATH}assembly_stats.py -i $transcripts -o ${STAT_FOLDER}assembly_qc/

echo BLAST_ASSEMBLY_QC: IN:$transcripts >> ${OUT_FOLDER}.LOG.txt
echo `date +%F\ %H:%M:%S` "END BLAST_ASSEMBLY_QC" >> ${OUT_FOLDER}.LOG.txt
