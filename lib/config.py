from collections import OrderedDict

VERSION = "0.11.1"

# A list of the paths used in the pipeline:

# for testing 
PIPE_PATH = "/home/ubuntu/server_side/"
OUT_FOLDER = "/gpfs/res_projects/cvcv/webserver/users/"

# for stable
#PIPE_PATH = "/var/genorama/server_side/stable/"
#OUT_FOLDER = "/gpfs/res_projects/cvcv/webserver/users/"

COMMAND_PATH = PIPE_PATH + "commands/"
PY_BIOLIB_PATH = "/gpfs/res_projects/cvcv/webserver/lib/"

BLAST_DB_FOLDER = "/gpfs/res_projects/cvcv/webserver/seq_dbs/"
HMMER_PROFILE_FOLDER = "/gpfs/res_projects/cvcv/webserver/seq_dbs/HMM_profiles/"

# put true to remove "unecessary" files for the user
MINIMAL_OUTPUT="TRUE"

# Docker

DOCKER_CLEANING="mycleaning"
DOCKER_ASSEMBLY="myassembly"
DOCKER_IDENTIFY="myidentification"

# Logging:
LOGFILEBYTES = 500*1024
# For testing:
LOGFILE="/home/ubuntu/server_side/trufa_pipe.log"

# For stable
#LOGFILE="/var/genorama/log/trufa_pipe.log"


# For stable:

# IDEA TO HAVE ALL JOB PARA IN A DICT BUT PROBLEM TO ASSIGN READS_FILES_COUNT and ENV
#JOBS_PARAMS = OrderedDict( [ ("FASTQC1", ["fastqc", "cleaning/fastqc.cmd", None, "2", "03:00:00", None ,"STAT/fastqc_report" ] ) ] )

