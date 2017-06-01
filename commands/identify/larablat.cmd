cd $IDENTIFICATION_FOLDER
db=`basename $BLAT_CONTIGS_DB`

mkdir blat_transcripts/$db

echo `date +%F\ %H:%M:%S` "START blat on assembly" >> ${OUT_FOLDER}.LOG.txt
echo "BLAT" $BLAT_TYPE "against" $db >> ${OUT_FOLDER}.LOG.txt


cd blat_transcripts/queries

for file in `ls`
do
    time srun --exclusive -n1 -N1 -c1 blat $BLAT_TYPE -out=blast8 \
	$file $BLAT_CONTIGS_DB ../$db/$file.b8 &

# To add when it will not take ages to run
#$PARAM_BLAT_FIN &

# BLAT_TYPE is replace by "-t=dnax -q=prot" for blatx for example
done
wait 

# cleaning and reporting to $OUT_FOLDER/blat_summary
cd ${IDENTIFICATION_FOLDER}blat_transcripts/$db
echo -e "QueryID\tDatabaseID(Subject)\t%ID\tAliLength\t#Mismatches\t#GapOpenings\tQueryStart\tQueryEnd\tSubjectStart\tSubjectEnd\tExpectValue\tBitScore" > blat_${db}_summary.txt
cat *.b8 >> blat_${db}_summary.txt
rm *.b8

# Getting the transcripts with hits
awk '{print $2}' blat_${db}_summary.txt | \
sort | uniq | wc -l | awk -v db=$db '{print db " hits: " $1}' - \
>> ${STAT_FOLDER}contigs_blat_summary.txt

echo `date +%F\ %H:%M:%S` "END blat on assembly" >> ${OUT_FOLDER}.LOG.txt
