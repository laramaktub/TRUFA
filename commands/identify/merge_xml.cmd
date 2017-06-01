module load PYTHON

echo `date +%F\ %H:%M:%S` "START xml merging" >> ${OUT_FOLDER}.LOG.txt

if [ -d ${IDENTIFICATION_FOLDER}blastplus_par/blast_out/ ]
then

    cd ${IDENTIFICATION_FOLDER}blastplus_par/blast_out/
    time ${PY_BIOLIB_PATH}work_on_xml.py *.xml > total.xml

    find . -type f -not -name "total.xml" -exec rm {} \;

else
    echo "ERROR EK: check the xml merging code"
fi

echo `date +%F\ %H:%M:%S` "END xml merging" >> ${OUT_FOLDER}.LOG.txt
