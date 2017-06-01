module load PYTHON
time srun --reservation=master_2017 --exclusive -n1 /home/cvcv/genorama/udocker run --env="DOCKER_CACHE_PATH=$CACHE_PATH" -v  /gpfs/res_projects/:/gpfs/res_projects -v /home/cvcv:/home/cvcv  $DOCKER_CLEANING /bin/bash  -c 'source $DOCKER_CACHE_PATH/tmp/script_dup_*'
