module load SAMTOOLS
module load PICARD_TOOLS
jars=/gpfs/res_apps/PICARD_TOOLS/1.79/

echo `date +%F\ %H:%M:%S` "START bam_postproc" >> ${OUT_FOLDER}.LOG.txt

#IO
#-------------------------------------------------------------------------------
sam=${ASSEMBLY_MAPPING_FOLDER}bowtie2/aligned_reads.sam
ref=$ASSEMBLY_FILE
bam=${ASSEMBLY_MAPPING_FOLDER}bowtie2/aligned_reads.bam

# Make index of assembly file if not there:
samtools faidx $ref

# SAM TO BAM CONVERSION (SAMTOOLS)
#-------------------------------------------------------------------------------
samtools view -Sbt ${ref}.fai $sam > $bam

# SORT BAMS BY COORDINATES (PICARD)
#-------------------------------------------------------------------------------
bam_out=${ASSEMBLY_MAPPING_FOLDER}bowtie2/aligned_reads_sort.bam
time srun --exclusive -c16 -n1 -N1 \
    java -jar ${jars}SortSam.jar \
    INPUT=$bam \
    OUTPUT=$bam_out \
    SORT_ORDER=coordinate &
    # if RAM issues:
    #MAX_RECORDS_IN_RAM=50000
wait

# REMOVE DUPLICATES (PICARD)
#-------------------------------------------------------------------------------
bam=$bam_out
bam_out=${ASSEMBLY_MAPPING_FOLDER}bowtie2/aligned_reads_sort_nodup.bam

time srun --exclusive -c16 -n1 -N1 \
    java -jar ${jars}MarkDuplicates.jar \
    INPUT=$bam \
    OUTPUT=$bam_out \
    METRICS_FILE=${ASSEMBLY_MAPPING_FOLDER}bowtie2/dupstat \
    REMOVE_DUPLICATES=true \
    MAX_FILE_HANDLES_FOR_READ_ENDS_MAP=900 &
wait

# FIX MATE INFO (PICARD)
#-------------------------------------------------------------------------------
bam=$bam_out
bam_out=${ASSEMBLY_MAPPING_FOLDER}bowtie2/aligned_reads_sort_nodup_mateok.bam
time srun --exclusive -c16 -n1 -N1 \
    java -jar ${jars}FixMateInformation.jar \
    INPUT=$bam \
    OUTPUT=$bam_out &
wait

if [ "$MINIMAL_OUTPUT" = "TRUE" ]
then
	cd ${ASSEMBLY_MAPPING_FOLDER}bowtie2
	rm aligned_reads_sort_nodup.bam
	rm aligned_reads_sort.bam
	rm aligned_reads.sam
fi

echo BAM_POSTPROC: SAM:$sam REF:$ref BAM:$bam_out >> ${OUT_FOLDER}.LOG.txt
echo `date +%F\ %H:%M:%S` "END bam_postproc" >> ${OUT_FOLDER}.LOG.txt