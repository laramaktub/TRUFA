
# Make a array out of the reads files string
reads_files=($READS_FILES)

index=bowtie2/index/myindex
sam_output=bowtie2/aligned_reads.sam
bam_output=bowtie2/aligned_reads

# This is a quick fix in case bowtie2 is used without specifying it
# i.e case where choosing only cufflinks or express
if [ -d $ASSEMBLY_MAPPING_FOLDER ]; then
    cd $ASSEMBLY_MAPPING_FOLDER
else
    mkdir $ASSEMBLY_MAPPING_FOLDER
    cd $ASSEMBLY_MAPPING_FOLDER
fi

mkdir bowtie2
mkdir bowtie2/index

echo `date +%F\ %H:%M:%S` "START bowtie2" >> ${OUT_FOLDER}.LOG.txt

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE
else
    echo "EK: check the bowtie2 code"
fi

#### Create the index:
time bowtie2-build $transcripts $index

if [ ${#reads_files[@]} -eq 2 ]; then
    reads1=${reads_files[0]}
    reads2=${reads_files[1]}

    mkdir bowtie2/hmgz

    time ${PY_BIOLIB_PATH}work_on_reads_new.py -r1 $reads1 -r2 $reads2 \
    -s -o bowtie2/hmgz/ 

    # get the correct inputs
    tmp=${reads1##*/}
    reads1=bowtie2/hmgz/${tmp%.*}_hmgz.fq
    reads_lonely=bowtie2/hmgz/${tmp%.*}_lonely.fq
    tmp=${reads2##*/}
    reads2=bowtie2/hmgz/${tmp%.*}_hmgz.fq
    
    time bowtie2 -x $index -1 $reads1 -2 $reads2 -U $reads_lonely -S $sam_output \
	-p 1 $PARAM_BOW2 \
	2> ${STAT_FOLDER}bowtie2.log

    echo BOWTIE2: R1:$reads1 R2:$reads2 S:$reads_lonely T:$transcripts PAR:$PARAM_BOW2 >> ${OUT_FOLDER}.LOG.txt

elif [ ${#reads_files[@]} -eq 1 ]; then
    reads_single=${reads_files[0]}

    time bowtie2 -x $index -U $reads_single -S $sam_output \
	-p 1 $PARAM_BOW2 \
	2> ${STAT_FOLDER}bowtie2.log

    echo BOWTIE2: R:$reads_single T:$transcripts PAR:$PARAM_BOW2 >> ${OUT_FOLDER}.LOG.txt

else
   echo `date +%F\ %H:%M:%S` "BOWTIE2 launching ERROR: visibly not 1 neither 2 input files specified, check bowtie.cmd" >> ${OUT_FOLDER}.LOG.txt
fi
wait

echo `date +%F\ %H:%M:%S` "END bowtie2" >> ${OUT_FOLDER}.LOG.txt

if [ "$MINIMAL_OUTPUT" = "TRUE" ]
then
	rm -r bowtie2/hmgz
	rm -r bowtie2/index
fi
