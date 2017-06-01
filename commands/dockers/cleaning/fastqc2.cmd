module load PYTHON
time srun --reservation=master_2017 --exclusive -n1 /home/cvcv/genorama/udocker run --env="DOCKER_CACHE_PATH=$CACHE_PATH" -v  /gpfs/csic_users/lara/:$HOME  $DOCKER_CLEANING /bin/bash  -c 'source $DOCKER_CACHE_PATH/tmp/script_fastqc2_*'
