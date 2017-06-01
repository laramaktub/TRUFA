
echo `date +%F\ %H:%M:%S` "BEGIN blat_parser" >> ${OUT_FOLDER}.LOG.txt

cd $CLEANING_FOLDER

time ${PY_BIOLIB_PATH}tidy_blat_results.py -reads $READS_FILES -folder $CLEANING_FOLDER -sum ${STAT_FOLDER}reads_blat_summary.txt

echo `date +%F\ %H:%M:%S` "END blat_parser" >> ${OUT_FOLDER}.LOG.txt


