module load TRINITY_RNA_SEQ

cd $ASSEMBLY_MAPPING_FOLDER

# Make a array out of the reads files string
reads_files=($READS_FILES)

echo `date +%F\ %H:%M:%S` "START Trinity" >> ${OUT_FOLDER}.LOG.txt

if [ ${#reads_files[@]} -eq 2 ]; then

    time Trinity.pl --seqType fq --JM 40G --CPU 16 --inchworm_cpu 16 --bflyCPU 7 --bflyHeapSpaceMax 8G \
	$PARAM_TRIN \
	--left ${reads_files[0]} \
	--right ${reads_files[1]} \
	--output trinity \
	--max_reads_per_graph 2000000
    echo TRINITY: IN:${reads_files[@]} PAR:$PARAM_TRIN >> ${OUT_FOLDER}.LOG.txt

elif [ ${#reads_files[@]} -eq 1 ]; then

    time Trinity.pl --seqType fq --JM 40G --CPU 16 --inchworm_cpu 16 --bflyCPU 7 --bflyHeapSpaceMax 8G \
	$PARAM_TRIN \
	--single ${reads_files[0]} \
	--output trinity \
	--max_reads_per_graph 2000000 
    echo TRINITY: IN:${reads_files[@]} PAR:$PARAM_TRIN >> ${OUT_FOLDER}.LOG.txt

else
    echo `date +%F\ %H:%M:%S` "TRINITY launching ERROR: visibly not 1 neither 2 input files specified, check Trinity.cmd" >> ${OUT_FOLDER}.LOG.txt
fi
wait 

#### Indexing fasta file:
module load SAMTOOLS
time samtools faidx trinity/Trinity.fasta

#### Cleaning unecessary files
if [ "$MINIMAL_OUTPUT" = "TRUE" ]
then
	find trinity/. -not -name "Trinity.fasta" \
	-not -name "." \
	-not -name "Trinity.fasta.fai" \
	-exec rm -r {} \;
fi

echo `date +%F\ %H:%M:%S` "END Trinity" >> ${OUT_FOLDER}.LOG.txt
