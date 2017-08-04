module load TRINITY_RNA_SEQ/r2013-11-10
module load PYTHON
module load RSEM

echo `date +%F\ %H:%M:%S` "START RSEM" >> ${OUT_FOLDER}.LOG.txt

#### Variables to specify automactically afterwards:
# Make a array out of the reads files string
reads_files=($READS_FILES)

#cd $ASSEMBLY_MAPPING_FOLDER

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE
else
    echo "ERROR: check the RSEM code" >> ${OUT_FOLDER}.LOG.txt
fi

cd $EXPRESSION_FOLDER
mkdir RSEM

if [ ${#reads_files[@]} -eq 2 ]; then
    reads1=${reads_files[0]}
    reads2=${reads_files[1]}

    mkdir RSEM/hmgz

    time ${PY_BIOLIB_PATH}work_on_reads_new.py -r1 $reads1 -r2 $reads2 \
    -s -o RSEM/hmgz/

    # get the correct inputs
    tmp=${reads1##*/}
    reads1=RSEM/hmgz/${tmp%.*}_hmgz.fq
    reads_lonely=RSEM/hmgz/${tmp%.*}_lonely.fq
    tmp=${reads2##*/}
    reads2=RSEM/hmgz/${tmp%.*}_hmgz.fq

# SO FAR: the RSEM command is using only the paired reads
# RSEM is not yet supporting a mix of single and paired reads 

    time $TRINITY_HOME/util/align_and_estimate_abundance.pl \
	--transcripts $transcripts \
	--seqType fq \
	--left $reads1 \
	--right $reads2 \
	--output_dir RSEM \
	-- --bowtie-chunkmbs 1000
#-- --fragment-length-max 500 >>> default in RSEM is 1000

    # Cleaning:
    rm -r RSEM/hmgz

    echo RSEM: R1:$reads1 R2:$reads2 T:$transcripts PAR:$PARAM_RSEM >> ${OUT_FOLDER}.LOG.txt

elif [ ${#reads_files[@]} -eq 1 ]; then
    reads_single=${reads_files[0]}

    time $TRINITY_HOME/util/align_and_estimate_abundance.pl \
	--transcripts $transcripts \
	--seqType fq \
	--single $reads_single \
	--output_dir RSEM 
#	-- --bowtie-chunkmbs 1000
#-- --fragment-length-max 500 >>> default in RSEM is 1000
    echo RSEM: R:$reads_single T:$transcripts PAR:$PARAM_RSEM >> ${OUT_FOLDER}.LOG.txt

else
   echo `date +%F\ %H:%M:%S` "RSEM launching ERROR: visibly not 1 neither 2 input files specified, check RSEM.cmd" >> ${OUT_FOLDER}.LOG.txt
fi

#### Statistics:

${PY_BIOLIB_PATH}expression_stats.py -g RSEM/RSEM.genes.results -i RSEM/RSEM.isoforms.results -o ${STAT_FOLDER}expression_stats/

#### Cleaning:
if [ "$MINIMAL_OUTPUT" = "TRUE" ]
then
    # GO to the folder of the used assembly file (trinity or )
    cd `dirname $ASSEMBLY_FILE`
    rm *.component_to_trans_map
    rm *.TRANS.*
fi

echo `date +%F\ %H:%M:%S` "END RSEM" >> ${OUT_FOLDER}.LOG.txt
