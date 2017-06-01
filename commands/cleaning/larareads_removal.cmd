
function reads_removal(){
    echo `date +%F\ %H:%M:%S` "START reads_removal" >> ${OUT_FOLDER}.LOG.txt
    cd $CLEANING_FOLDER

    reads_in=($READS_FILES)
    reads_out=($READS_OUT)
    
    for ((i=0; i<${#reads_in[@]}; i++)); do

	file_id=`basename ${reads_in[ i]}`
	reads2remove=blat_${file_id}/out_blat/reads_to_remove.txt
	myinput=${reads_in[ i ]}
	
# The script removing bad reads:
	echo "reads_suppresor_bin.py for:" $file_id >> ${OUT_FOLDER}.LOG.txt
	${PY_BIOLIB_PATH}reads_suppresor_bin.py \
	    $reads2remove $myinput > ${reads_out[ i ]}

# For the LOG and check if reads_suppressor_bin is working correctly
# WARNING: THIS PART SEEMS TO BE WAY TO SLOW (MAKE TO JOB CANCEL SOMETIMES)
	echo `date +%F\ %H:%M:%S` "Reads removed counts for:" $file_id
	before_num=`${PY_BIOLIB_PATH}reads_counter.py $myinput`
	rm_num=`wc -l < $reads2remove`
	after_num=`${PY_BIOLIB_PATH}reads_counter.py ${reads_out[i]}`
	my_check=`expr $before_num - $rm_num - $after_num`

	if [ "$my_check" -ne 0 ] # in the case the number of reads removed is not correct
	then
	    echo "Check reads_removal_bin.py. Something is wrong in the count of removed reads" >> ${OUT_FOLDER}.LOG.txt
	fi

	echo $before_num $myinput "reads before Blat cleaning" >> $STAT_FOLDER${file_id}_blat.log.txt
	echo $rm_num "total reads removed by Blat cleaning" >> $STAT_FOLDER${file_id}_blat.log.txt
	echo $after_num "total reads left" >> $STAT_FOLDER${file_id}_blat.log.txt

	# Cleaning: now removes everything, check if blat results could be usefull for user ?
	rm -r blat_${file_id}

    done
}

time reads_removal

echo `date +%F\ %H:%M:%S` "END reads_removal" >> ${OUT_FOLDER}.LOG.txt
