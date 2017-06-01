module load TRINITY_RNA_SEQ

cd $ASSEMBLY_MAPPING_FOLDER
mkdir bowtie

echo `date +%F\ %H:%M:%S` "START bowtie" >> ${OUT_FOLDER}.LOG.txt

# Make a array out of the reads files string
reads_files=($READS_FILES)
transcripts=$ASSEMBLY_FILE

if [ ${#reads_files[@]} -eq 2 ]; then

    time /gpfs/res_apps/TRINITY_RNA_SEQ/r2012-06-08/util/alignReads.pl \
	--seqType fq --left ${reads_files[0]} --right ${reads_files[1]} \
	--target $transcripts -o bowtie --aligner bowtie \
	-- -p 16 --un unaligned_reads --al aligned_reads $PARAM_BOW

    echo BOWTIE1: R1:${reads_files[0]} R2:${reads_files[1]} T:$transcripts \
PAR:$PARAM_BOW >> ${OUT_FOLDER}.LOG.txt

elif [ ${#reads_files[@]} -eq 1 ]; then

    time /gpfs/res_apps/TRINITY_RNA_SEQ/r2012-06-08/util/alignReads.pl \
	--seqType fq --single ${reads_files[0]} --target $transcripts -o bowtie --aligner bowtie -- -p 16 --un unaligned_reads --al aligned_reads $PARAM_BOW
    echo BOWTIE1: R:${reads_files[0]} T:$transcripts PAR:$PARAM_BOW \
	>> ${OUT_FOLDER}.LOG.txt

else
   echo `date +%F\ %H:%M:%S` "BOWTIE launching ERROR: visibly not 1 neither 2 input files specified, check bowtie.cmd" >> ${OUT_FOLDER}.LOG.txt
fi
wait

echo `date +%F\ %H:%M:%S` "END bowtie" >> ${OUT_FOLDER}.LOG.txt
