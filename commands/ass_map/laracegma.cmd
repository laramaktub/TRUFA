
echo `date +%F\ %H:%M:%S` "START CEGMA" >> ${OUT_FOLDER}.LOG.txt

cd $ASSEMBLY_MAPPING_FOLDER

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE

else
    echo "EK: check the cegma code"
fi


cd ${STAT_FOLDER}assembly_qc/cegma

time cegma -g $transcripts -o cegma -T 16

echo CEGMA: IN:$transcripts >> ${OUT_FOLDER}.LOG.txt
echo `date +%F\ %H:%M:%S` "END CEGMA" >> ${OUT_FOLDER}.LOG.txt

