
echo `date +%F\ %H:%M:%S` "START EXPRESS" >> ${OUT_FOLDER}.LOG.txt

# IO:
#-------------------------------------------------------------------------------
ref=$ASSEMBLY_FILE
bam=${ASSEMBLY_MAPPING_FOLDER}hisat2/aligned_reads_sort_nodup_mateok.bam
mkdir ${EXPRESSION_FOLDER}express
bam_tmp=${EXPRESSION_FOLDER}express/aligned_reads_rsort4express
#-------------------------------------------------------------------------------

# SORT BY READS IDS (NECESSARY FOR EXPRESS)
#-------------------------------------------------------------------------------

echo Sorting by reads ID for express: bam_in:$bam bam_out:$bam_tmp 
samtools sort -n $bam -o $bam_tmp &
wait

# EXPRESS
#-------------------------------------------------------------------------------

echo EXPRESS: REF:$ref BAM:$bam_tmp >> ${OUT_FOLDER}.LOG.txt
 express $ref ${bam_tmp}.bam \
    -o ${EXPRESSION_FOLDER}express &
	#-m 600 
wait


#CLEANING
#-------------------------------------------------------------------------------
rm ${bam_tmp}.bam

#### Statistics:
# TO ADD 

echo `date +%F\ %H:%M:%S` "END EXPRESS" >> ${OUT_FOLDER}.LOG.txt
