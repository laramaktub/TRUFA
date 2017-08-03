echo `date +%F\ %H:%M:%S` "START splitting" >> ${OUT_FOLDER}.LOG.txt

if [ -n "$ASSEMBLY_FILE" ]
then
    infile=$ASSEMBLY_FILE
else
    echo "EK: check the splitting code"
fi

cd $IDENTIFICATION_FOLDER
mkdir blat_transcripts/
mkdir blat_transcripts/queries

${PY_BIOLIB_PATH}fasta_split4blat.py $infile blat_transcripts/queries/contigs.splitted 64 &

wait
echo `date +%F\ %H:%M:%S` "END splitting" >> ${OUT_FOLDER}.LOG.txt
