
echo `date +%F\ %H:%M:%S` "START splitting for HMMER" >> ${OUT_FOLDER}.LOG.txt

if [ -n "$ASSEMBLY_FILE" ]
then
    infile=$ASSEMBLY_FILE
else
    echo "EK: check the splitting for hmmer code"
fi

cd $IDENTIFICATION_FOLDER
mkdir hmmer_transcripts/
mkdir hmmer_transcripts/queries

# Translation nucleotides to AA:
# TODO: implement different techniques to get the translation

${PY_BIOLIB_PATH}translation.py $infile hmmer_transcripts/AA_contigs.fas

# Cut the contig file in 6 

${PY_BIOLIB_PATH}fasta_split4blat.py hmmer_transcripts/AA_contigs.fas hmmer_transcripts/queries/contigs.splitted 6 &

wait
echo `date +%F\ %H:%M:%S` "END splitting for HMMER" >> ${OUT_FOLDER}.LOG.txt

