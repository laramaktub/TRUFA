# Make a array out of the reads files string
reads_files=($READS_FILES)

index=hisat2/index/myindex
sam_output=hisat2/aligned_reads.sam

# This is a quick fix in case hisat2 is used without specifying it
# i.e case where choosing only cufflinks or express
if [ -d $ASSEMBLY_MAPPING_FOLDER ]; then
    cd $ASSEMBLY_MAPPING_FOLDER
else
    mkdir $ASSEMBLY_MAPPING_FOLDER
    cd $ASSEMBLY_MAPPING_FOLDER
fi

mkdir hisat2
mkdir hisat2/index

echo `date +%F\ %H:%M:%S` "START hisat2" >> ${OUT_FOLDER}.LOG.txt

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE
else
    echo "EK: check the hisat2 code"
fi

#### Create the index:
time hisat2-build -p 16 $transcripts $index


if [ ${#reads_files[@]} -eq 2 ]; then
    reads1=${reads_files[0]}
    reads2=${reads_files[1]}

    mkdir hisat2/hmgz

    time ${PY_BIOLIB_PATH}work_on_reads_new.py -r1 $reads1 -r2 $reads2 \
    -s -o hisat2/hmgz/ 

    # get the correct inputs
    tmp=${reads1##*/}
    reads1=hisat2/hmgz/${tmp%.*}_hmgz.fq
    reads_lonely=hisat2/hmgz/${tmp%.*}_lonely.fq
    tmp=${reads2##*/}
    reads2=hisat2/hmgz/${tmp%.*}_hmgz.fq
    
    time hisat2 -x $index -1 $reads1 -2 $reads2 -U $reads_lonely -S $sam_output \
	-p 16 $PARAM_HISAT2 \
	2> ${STAT_FOLDER}hisat2.log

			

    echo HISAT2: R1:$reads1 R2:$reads2 S:$reads_lonely T:$transcripts PAR:$PARAM_BOW2 >> ${OUT_FOLDER}.LOG.txt

elif [ ${#reads_files[@]} -eq 1 ]; then
    reads_single=${reads_files[0]}

    time hisat2 -x $index -U $reads_single -S $sam_output \
	-p 16 $PARAM_HISAT2 \
	2> ${STAT_FOLDER}hisat2.log

    echo HISAT2: R:$reads_single T:$transcripts PAR:$PARAM_HISAT2 >> ${OUT_FOLDER}.LOG.txt

else
   echo `date +%F\ %H:%M:%S` "HISAT2 launching ERROR: visibly not 1 neither 2 input files specified, check hisat2.cmd" >> ${OUT_FOLDER}.LOG.txt
fi
wait

echo `date +%F\ %H:%M:%S` "END hisat2" >> ${OUT_FOLDER}.LOG.txt

if [ "$MINIMAL_OUTPUT" = "TRUE" ]
then
	rm -r hisat2/hmgz
	rm -r hisat2/index
fi
