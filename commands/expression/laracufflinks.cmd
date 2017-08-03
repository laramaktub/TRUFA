
#### Make the GFF file:
# This is only working with Trinity now !

cd $ASSEMBLY_MAPPING_FOLDER

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE

else
    echo "EK: check the cufflinks code"
fi

gff_file=${EXPRESSION_FOLDER}tmp.gff
outfolder=${EXPRESSION_FOLDER}cufflinks

mkdir $outfolder

time ${PY_BIOLIB_PATH}work_on_assemblies_2.py $transcripts -gff > $gff_file

#-------------------------------------------------------------------------------

time cufflinks ${ASSEMBLY_MAPPING_FOLDER}bowtie2/aligned_reads.bam \
-G $gff_file \
-o $outfolder -p 16


#### Statistics:

${PY_BIOLIB_PATH}expression_stats.py -c ${outfolder}/isoforms.fpkm_tracking -o ${STAT_FOLDER}expression_stats/
