module load INTERPROSCAN

cd $IDENTIFICATION_FOLDER

# not sure this is necessary > default /tmp (check ipscan -h) should work
mkdir TMP_INTERPROSCAN
export INTERPROSCAN_TMPDIR=${OUT_FOLDER}TMP_INTERPROSCAN

echo `date +%F\ %H:%M:%S` "START Interproscan for B2GO on assembly" >> ${OUT_FOLDER}.LOG.txt


cd ${IDENTIFICATION_FOLDER}ipscan/queries
mkdir ../out

for file in `ls`
do
    time srun --exclusive -n1 -N1 interproscan.sh -t n -i $file -o ../out/$file.out -f xml &
done

# -t n is for nucleotide input

wait

rm -r $OUT_FOLDER/TMP_INTERPROSCAN

echo `date +%F\ %H:%M:%S` "END Interproscan on assembly for B2GO" >> ${OUT_FOLDER}.LOG.txt