module load BLASTP
module load PYTHON

echo `date +%F\ %H:%M:%S` "START BLAST+" >> ${OUT_FOLDER}.LOG.txt

#### PREPARING OUTPUT FOLDERS
cd ${IDENTIFICATION_FOLDER}blastplus_par
mkdir splitted
mkdir blast_out

#### PREPARE QUERIES:

if [ -n "$ASSEMBLY_FILE" ]
then
${PY_BIOLIB_PATH}fasta_split4blat.py $ASSEMBLY_FILE splitted/query_split 16

else
    echo "EK: check the blastplus code"
fi


#### IO:
db=/gpfs/res_projects/cvcv/webserver/seq_dbs/nr_blastplus/nr

#### JOB:
for q in `find splitted/query_split*`
do
    tmp=${q##*/}
    out=blast_out/${tmp%%.*}_out.xml
    echo BLASTING $q
    echo OUTPUT IN $out
    
    time srun --exclusive -N1 -n1 blastx \
    	-query $q -db $db \
    	-out $out -evalue 1e-6 -num_threads 16 \
    	-outfmt 5 \
    	-max_target_seqs 100 &
done
wait

#### Cleaning unecessary files
if [ "$MINIMAL_OUTPUT" = "TRUE" ]
then
    rm -r splitted
fi

echo BLAST+: QUERY: $ASSEMBLY_FILE DB: $db >> ${OUT_FOLDER}.LOG.txt
echo `date +%F\ %H:%M:%S` "END BLAST+" >> ${OUT_FOLDER}.LOG.txt
