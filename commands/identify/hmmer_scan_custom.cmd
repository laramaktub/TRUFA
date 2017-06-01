module load HMMER

cd $IDENTIFICATION_FOLDER
mkdir hmmer_transcripts/$HMM_PROFILE

echo `date +%F\ %H:%M:%S` "START HMMer on assembly" >> ${OUT_FOLDER}.LOG.txt
echo -e "HMMer against $HMM_PROFILE" >> ${OUT_FOLDER}.LOG.txt

# For each files coming from the splitting step:

cd hmmer_transcripts/queries

for file in `ls`
do
# With Hmmer 3.0 (hmmpfam for previous versions)
    time srun --exclusive -n1 -N1 -c16 hmmscan \
	--tblout ../$HMM_PROFILE/$file.out.tab \
	--cpu 16 $HMM_PATH $file &

# > not working > to send an email to HMMER people
#--domtblout ../$HMM_PROFILE/$file.out.tab \

done
wait

# Concatenate all splitted outputs and keep the header (3 first lines)
cd ../$HMM_PROFILE/
awk 'FNR==1 && NR!=1 { while (/^#/) getline;} 1 {print}' *.tab > hmmer_results.tab.txt
rm *.out.tab

echo `date +%F\ %H:%M:%S` "END HMMer on assembly" >> ${OUT_FOLDER}.LOG.txt

