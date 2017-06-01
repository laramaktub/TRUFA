if [ -e "${IDENTIFICATION_FOLDER}blat_transcripts/" ]; then
    cd ${IDENTIFICATION_FOLDER}blat_transcripts/
    rm -r queries
    
else
    echo "WARNING BLAT_CLEANING: ${IDENTIFICATION_FOLDER}blat_transcripts/ folder not found for deletion" \
	>> ${OUT_FOLDER}.LOG.txt
fi
