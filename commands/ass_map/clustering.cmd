cd $ASSEMBLY_MAPPING_FOLDER
mkdir cdhitest

echo `date +%F\ %H:%M:%S` "START CDHITEST" >> ${OUT_FOLDER}.LOG.txt

#IO
if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE

else
    echo "EK: check the cdhitest code"
fi

out=cdhitest/assembly_clust.fas

# CD-HIT-EST 
time ${PY_BIOLIB_PATH}cdhit/cd-hit-est -i $transcripts -o $out \
$PARAM_CDHITEST -M 0 -T 16 -c 0.95 -r 1

rm ${out}.bak.clstr
mv ${out}.clstr cdhitest/clustering.log.txt

echo CDHITEST: IN:$transcripts OUT:${ASSEMBLY_MAPPING_FOLDER}$out >> ${OUT_FOLDER}.LOG.txt
echo `date +%F\ %H:%M:%S` "END CDHITEST" >> ${OUT_FOLDER}.LOG.txt
