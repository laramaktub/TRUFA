if [ -e "${IDENTIFICATION_FOLDER}hmmer_transcripts/" ]; then
    cd ${IDENTIFICATION_FOLDER}hmmer_transcripts/
    rm -r queries
    
else
    echo "WARNING HMMER_CLEANING: ${IDENTIFICATION_FOLDER}hmmer_transcripts/ folder not found for deletion" \
	>> ${OUT_FOLDER}.LOG.txt
fi
