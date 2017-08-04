module load PYTHON

time srun --reservation=master_2017 --exclusive -n1 /home/cvcv/genorama/udocker run --env="DOCKER_CACHE_PATH=$CACHE_PATH" -v  /gpfs/res_projects/:/gpfs/res_projects -v /home/cvcv:/home/cvcv -v /gpfs/res_apps/:/gpfs/res_apps $DOCKER_ASSEMBLY /bin/bash  -c 'source $DOCKER_CACHE_PATH/tmp/script_bam_postproc*'
