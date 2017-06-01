module load JAVA

# Have to add the ext folder and the blast2go.jar in the working folder apparently
# the img option [ -img ] (causing errors I think because of no X11) has been suppressed (to check what is was for !)

echo `date +%F\ %H:%M:%S` "START B2GO" >> ${OUT_FOLDER}.LOG.txt

mkdir ${IDENTIFICATION_FOLDER}b2go
cd ${PY_BIOLIB_PATH}b2go

# Copying B2GO property file for each run personnal use
cp ${PY_BIOLIB_PATH}b2go/b2gPipe.properties_new ${IDENTIFICATION_FOLDER}b2go/b2gPipe.properties

if [ -e ${IDENTIFICATION_FOLDER}blastplus_par/blast_out/total.xml ]
then
    xml_in=${IDENTIFICATION_FOLDER}blastplus_par/blast_out/total.xml

    if [ -d ${IDENTIFICATION_FOLDER}ipscan/out ]
    then
	echo " ipscan results integrations to b2Go not done yet(2)" >> ${OUT_FOLDER}.LOG.txt
    else
	time java -cp *:ext/*: es.blast2go.prog.B2GAnnotPipe \
	    -in $xml_in \
	    -out ${IDENTIFICATION_FOLDER}b2go/out_b2go \
	    -prop ${IDENTIFICATION_FOLDER}b2go/b2gPipe.properties \
	    -v -annot -dat -annex

	echo B2GO: XML_IN:$xml_in >> ${OUT_FOLDER}.LOG.txt
    fi

else
    echo "Something is wrong with b2go cmd" >> ${OUT_FOLDER}.LOG.txt

fi

# -goslim >>> not working because no internet connection >>> ask luis

echo `date +%F\ %H:%M:%S` "END B2GO" >> ${OUT_FOLDER}.LOG.txt
