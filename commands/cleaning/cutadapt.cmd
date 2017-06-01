module load CUTADAPT
echo `date +%F\ %H:%M:%S` "START cutadapt" >> ${OUT_FOLDER}.LOG.txt

cd $CLEANING_FOLDER		

reads_in=($READS_FILES)
reads_out=($READS_OUT)

for ((i=0; i<${#reads_in[@]}; i++)); do

    time srun --exclusive -n1 -c16 -N1 \
	${PY_BIOLIB_PATH}cutadapt \
	${reads_in[i]} \
	-o ${reads_out[i]} \
	$PARAM_CUTADAPT &

    echo CUTADAPT: IN: ${reads_in[ i ]} OUT: ${reads_out[ i ]} \
	PAR: $PARAM_CUTADAPT >> ${OUT_FOLDER}.LOG.txt
done
wait
echo `date +%F\ %H:%M:%S` "END cutadapt" >> ${OUT_FOLDER}.LOG.txt
