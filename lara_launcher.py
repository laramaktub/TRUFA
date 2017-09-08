#! /usr/bin/env python

# THINGS TO IMPROVE:


# THINGS TO IMPROVE:
# in bowtie 2 command, check the output files names (the first linesof the cmd)
# remove env variables (not used the same way anymore) <<< not sure about that
# Make better the import of the parameters (without having to delete the other entries in sort_parameters)

# THINGS TO VERIFY (TESTING PARAMETERS NOT CORRECT FOR REAL USE)
# input files (reads)

#-------------------------------------------------------------------------------
import logging
import logging.handlers
import sys
import os
import getopt
import mimetypes
import time
from lib import submiting_jobs as sj
from lib import soft_data
from lib import config
from lib import run_config
#from lib import common_fun

#-------------------------------------------------------------------------------
def configLog():
    # get logger
    logger = logging.getLogger()
    
    # create file handler
    ch = logging.handlers.RotatingFileHandler( config.LOGFILE, mode='a', maxBytes=config.LOGFILEBYTES, backupCount=5 )
    
    ch.setLevel( logging.DEBUG )
    
    # create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s -%(levelname)s- %(message)s',
        datefmt='%Y%m%d %H:%M:%S' )
    
    # add formatter to ch
    ch.setFormatter( formatter )
    
    # add ch to logger
    logger.addHandler( ch )
    
    logging.captureWarnings( True )

#-------------------------------------------------------------------------------
def checkIfCommandLine():
    """ Check if command line or webserver version.
    For command line: edit run_config in lib and launch ./pipe_launcher -c """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c")
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
        
    for o, a in opts:
        if o == "-c":
            return True
        else:
            return False
            
#-------------------------------------------------------------------------------
def setUidJid(COMMAND_MODE):
    if COMMAND_MODE:
        print "Launching in command line mode"
        REALUSER = run_config.REALUSER
        job_num = run_config.JOB_NUM
        para_dict = run_config.para_dict
        DEBUG = run_config.DEBUG
        #    common_fun.check_inputs_format(para_dict)
    
    else: # if run by webserver
        print "Launched by the webserver"
        DEBUG = False 
        REALUSER, para_dict = sj.get_parameters(sys.argv[1],sys.argv[2])
        job_num = sys.argv[-1]

    return REALUSER, job_num, para_dict, DEBUG

#-------------------------------------------------------------------------------
def setPaths():
    OUT_FOLDER = config.OUT_FOLDER + REALUSER + "/jobs/Job_" + job_num + "/"
    DATA_FOLDER = config.OUT_FOLDER + REALUSER + "/data/"

    folders_dict = dict(OUT_FOLDER = OUT_FOLDER,
                        DATA_FOLDER = DATA_FOLDER,
                        CACHE_PATH = OUT_FOLDER + ".cache/",
                        CLEANING_FOLDER = OUT_FOLDER + "CLEANING/",
                        STAT_FOLDER = OUT_FOLDER + "STAT/",
                        ASSEMBLY_MAPPING_FOLDER = OUT_FOLDER + "ASSEMBLY_MAPPING/",
                        IDENTIFICATION_FOLDER = OUT_FOLDER + "IDENTIFICATION/",
                        EXPRESSION_FOLDER = OUT_FOLDER + "EXPRESSION/",
                        PIPE_PATH = config.PIPE_PATH,
                        PY_BIOLIB_PATH = config.PY_BIOLIB_PATH,
                        COMMAND_PATH = config.COMMAND_PATH,
                        DOCKER_CLEANING= config.DOCKER_CLEANING,
                        DOCKER_ASSEMBLY= config.DOCKER_ASSEMBLY,
                        DOCKER_IDENTIFY= config.DOCKER_IDENTIFY)

    COMMAND_PATH = config.COMMAND_PATH
    BLAST_DB_FOLDER = config.BLAST_DB_FOLDER
    HMMER_PROFILE_FOLDER = config.HMMER_PROFILE_FOLDER

    return folders_dict, COMMAND_PATH, BLAST_DB_FOLDER, HMMER_PROFILE_FOLDER

#-------------------------------------------------------------------------------
def makeOutputFolders(folders_dict):

    try:
        os.makedirs(folders_dict["OUT_FOLDER"])
        os.makedirs(folders_dict["CACHE_PATH"])
        os.mkdir(folders_dict["CACHE_PATH"] + "tmp")
        os.mkdir(folders_dict["STAT_FOLDER"])
        os.mkdir(folders_dict["OUT_FOLDER"] + "log")
    except Exception as e:
        logging.error(e)
        sys.exit()

#-------------------------------------------------------------------------------
def getInput(para_dict):
    input_dict = sj.sort_parameters(para_dict)
    READS_FILES = input_dict["reads_files"]
    READS_FILES_COUNT = len(READS_FILES)
    BLATN_CUSTOM_READS = input_dict["blatn_reads"]
    BLATN_CUSTOM_ASS = input_dict["blatn_ass"]
    BLATX_CUSTOM_ASS = input_dict["blatx_ass"]
    HMMER_CUSTOM_DB = input_dict["hmm_custom_db"]

    return input_dict, READS_FILES, READS_FILES_COUNT, BLATN_CUSTOM_READS,BLATN_CUSTOM_ASS, BLATX_CUSTOM_ASS, HMMER_CUSTOM_DB

#-------------------------------------------------------------------------------
def setBashEnv(input_dict, folders_dict):
    env = sj.set_environment(input_dict, folders_dict)
    env["MINIMAL_OUTPUT"]=config.MINIMAL_OUTPUT
    env["FILE_SYSTEM"]=config.FILE_SYSTEM
    # Add for MPIBLAST:
    #env["BLASTMAT"]="/mnt/seq_dbs/matrices"
    #env["MPIBLAST_SHARED"]="/mnt/seq_dbs/nr"
    #env["MPIBLAST_LOCAL"]=folders_dict["IDENTIFICATION_FOLDER"] + ""

    return env

#-------------------------------------------------------------------------------
def checkIfCompressedReads(folders_dict, READS_FILES):
    new_READS_FILES = []

    with open(folders_dict["OUT_FOLDER"] + ".tmp1.txt", "a") as f:
        files_to_unzip = []

        for rf in READS_FILES:
            raw = rf
            rf = rf.split( os.extsep, 2 )
            fname = ".".join( rf[:2] )
            ext = rf[-1]

            # Check extension:
            if ext in ["gz","tar.gz"]:
                f.write("File: {0} is set for extraction\n".format(raw))
                files_to_unzip.append(raw)
                new_READS_FILES.append(fname)
            else:
                f.write("""File: {0} doesn't seem to be a compressed file,
                        or his extension is not recognized, so it will be considered
                        as a 'directly usable' file\n""".format(raw))
                new_READS_FILES.append(raw)

    return new_READS_FILES, files_to_unzip

#-------------------------------------------------------------------------------
def extract(files_to_unzip, OUT_FOLDER, COMMAND_PATH, dep):
    env["FILES_TO_UNZIP"] = "'" + " ".join(files_to_unzip) + "'"
    job_id = sj.make_and_submit_job(OUT_FOLDER,
                                    COMMAND_PATH + "extract2.cmd",
                                    "extract", 1,
                                    1, "12:00:00","", env)
#    slurm_ids.append(job_id)
    dep.append(job_id)
    return dep

#-------------------------------------------------------------------------------
class TrufaJob():
    """
    To define better names
    HERE:
    jobfolder is for the whole Job, composed of TrufaJobs e.g; OUT_FOLDER
    outfolder is the outfolder of the TrufaJob: STAT_FOLDER/fastqc_report
    """
    def __init__(self, name, command, dep, jobfolder, ntasks, ncpus, tlim, env, outfolder=None):
        self.name = name
        self.command_path = config.COMMAND_PATH + command
        self.dep = dep
        self.jobfolder = jobfolder
        self.outfolder = outfolder
        self.ntasks = ntasks
        self.ncpus = ncpus
        self.tlim = tlim
        self.env = env

    def makeOutFolder(self):
        if self.outfolder:
            if not os.path.exists(self.outfolder):
                os.makedirs(self.outfolder)
            else:
                print self.name
                print self.outfolder + " already exists: not created (it's fine)."

    
    def script(self):
        sj.make_script(self.jobfolder,
                                       	self.command_path,
                                       	self.name,
                                       	self.ntasks,
                                       	self.ncpus,
                                        self.tlim,
                                        self.dep,
                                       	self.env,
                                        DEBUG)
        


    def submit(self):
        job_id = sj.make_and_submit_job(self.jobfolder,
                                        self.command_path,
                                        self.name,
                                        self.ntasks,
                                        self.ncpus,
                                        self.tlim,
                                        self.dep,
                                        self.env,
                                        DEBUG)
        
        return job_id

#-------------------------------------------------------------------------------
def prepareAndSubmit( jobname, cmd, dep, jobfolder, ntasks, cpus, tlim, env, outfolder=None):
    """
    Prepare the outfolders and submit a TrufaJob
    """

    try:
        job = TrufaJob( jobname, cmd, dep, jobfolder, ntasks, cpus, tlim, env, outfolder)
        job.makeOutFolder()
        slurm_id = job.submit()
    except Exception as e:
        print e
        print "Entra en la excepcion"
        logging.error(e)
        sys.exit()
    return slurm_id

#------------------------------------------------------------------------------
def prepareScript( jobname, cmd, dep, jobfolder, ntasks, cpus, tlim, env, outfolder=None):
    """
    Prepare the outfolders and submit a TrufaJob
    """
    try:
        scripttrufa = TrufaJob( jobname, cmd, dep, jobfolder, ntasks, cpus, tlim, env, outfolder)
        scripttrufa.makeOutFolder()
        slurm_id=scripttrufa.script()

    except Exception as e:
        logging.error(e)
        sys.exit()
        
    return slurm_id


    
#-------------------------------------------------------------------------------
def setReadOut( names_in, suffix):
    """ To setup the names of the output for the cleaning steps
    """
    # Setup the reads files basenames for the cleaning outputs
    
    names_in = names_in.replace("'", "").split(" ")
    ext = [ os.path.splitext(x)[-1] for x in names_in ]
    basenames = [ os.path.splitext(os.path.basename(x))[0]
                       for x in names_in ]
    names_out = "'" + " ".join( [ x + suffix + y
                                  for x, y in zip(basenames, ext) ] ) + "'"

    return names_out

#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------
logging.getLogger().setLevel( logging.DEBUG )
configLog()
logging.info("Start server side")
    
# INIT VAR: # Not in the same line  because of issues with values assignments 
slurm_ids = []
dep = []
blat_dep = []
hmmer_dep = []
b2go_dep = []
expr_dep = []

COMMAND_MODE = checkIfCommandLine()
REALUSER, job_num, para_dict, DEBUG = setUidJid(COMMAND_MODE)
folders_dict, COMMAND_PATH, BLAST_DB_FOLDER, HMMER_PROFILE_FOLDER = setPaths()
makeOutputFolders(folders_dict)
input_dict, READS_FILES, READS_FILES_COUNT, BLATN_CUSTOM_READS,BLATN_CUSTOM_ASS, BLATX_CUSTOM_ASS, HMMER_CUSTOM_DB = getInput(para_dict)

steps = input_dict["progs"]
env = setBashEnv(input_dict, folders_dict)

# Make LOG for debugging
sj.make_log(REALUSER, input_dict, folders_dict["OUT_FOLDER"] + ".tmp1.txt")

# Check and file decompression
new_READS_FILES, files_to_unzip = checkIfCompressedReads(folders_dict, READS_FILES)

if files_to_unzip and not DEBUG:
    dep = extract(files_to_unzip, folders_dict["OUT_FOLDER"], COMMAND_PATH, dep)

# Resetting READS_FILES variable to point to extracted files
env["READS_FILES"] = "'" + " ".join(new_READS_FILES) + "'"

#-------------------------------------------------------------------------------
if "FASTQC1" in steps:
    #Generate the docker job
    prepareScript("fastqc",
                                "cleaning/larafastqc.cmd",
                                dep,
                                folders_dict["OUT_FOLDER"],
                                READS_FILES_COUNT,2,"03:00:00",env,
                                folders_dict["STAT_FOLDER"] + "fastqc_report")

    slurm_id = prepareAndSubmit("fastqc",
                                "dockers/cleaning/fastqc.cmd",
                                dep,
                                folders_dict["OUT_FOLDER"],
                                READS_FILES_COUNT,2,"03:00:00",env,
                                folders_dict["STAT_FOLDER"] + "fastqc_report")
    slurm_ids.append( slurm_id )
    
    
    # Fastqc doesn't have to be incorporated in the dependency list
#-------------------------------------------------------------------------------
# If any program of the cleaning step is on:
if soft_data.cleaning_progs & steps:

    os.mkdir(folders_dict["CLEANING_FOLDER"])
#-------------------------------------------------------------------------------
    if "CUTADAPT" in steps:

        env["READS_OUT"] = setReadOut( env["READS_FILES"], "_noad" )
        prepareScript("cutadapt",
                                "cleaning/laracutadapt.cmd",
                                dep,
                                folders_dict["OUT_FOLDER"],
                                READS_FILES_COUNT,16,"06:00:00", env)

        slurm_id = prepareAndSubmit("cutadapt",
                                    "dockers/cleaning/cutadapt.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT,16,"06:00:00", env)
        
        slurm_ids.append(slurm_id)
        dep.append(slurm_id)

        # Set input for next step:
        env["READS_FILES"] = env["READS_OUT"]

#-------------------------------------------------------------------------------
    if "DUP" in steps:
        env["READS_OUT"] = setReadOut( env["READS_FILES"], "_nodup" )

        prepareScript("dup_prinseq",
                                    "cleaning/laraprinseq_dup.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "24:00:00", env)
	
        slurm_id = prepareAndSubmit("dup_prinseq",
                                    "dockers/cleaning/prinseq_dup.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "24:00:00", env)

        slurm_ids.append(slurm_id)
        dep.append(slurm_id)
        # Set input for next step:
        env["READS_FILES"] = env["READS_OUT"]

#-------------------------------------------------------------------------------
    if "TRIM" in steps:

        env["READS_OUT"] = setReadOut( env["READS_FILES"], "_trim" )


        prepareScript("trim_prinseq",
                                    "cleaning/laraprinseq_trim.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT, 16, "72:00:00", env)
        slurm_id = prepareAndSubmit("trim_prinseq",
                                    "dockers/cleaning/prinseq_trim.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT, 16, "72:00:00", env)

        slurm_ids.append(slurm_id)
        dep.append(slurm_id)

        # Set input for next step:
        env["READS_FILES"] = env["READS_OUT"]
#-------------------------------------------------------------------------------
# if there is any BLAT for the reads:
    if soft_data.blat_reads_progs & steps:
        env["READS_OUT"] = setReadOut( env["READS_FILES"], "_blat" )

    # Convert to fasta:
        prepareScript("fq2fas",
                                    "cleaning/larafq2fas.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT, 4, "1:00:00", env)

        slurm_id = prepareAndSubmit("fq2fas",
                                    "dockers/cleaning/fq2fas.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT, 4, "1:00:00", env)

        slurm_ids.append(slurm_id)
        dep.append(slurm_id)

    # Split for faster BLAT:
        prepareScript("split4rblat",
                                   "cleaning/larasplitting.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT, 4, "1:00:00", env)

        slurm_id = prepareAndSubmit("split4rblat",
                                    "dockers/cleaning/splitting.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    READS_FILES_COUNT, 4, "1:00:00", env)
        slurm_ids.append(slurm_id)
        dep.append(slurm_id)

#-------------------------------------------------------------------------------
        if "BLAT_UNIVEC" in steps:
            env["BLAT_READS_DB"] = BLAST_DB_FOLDER + "univec/univec"
            env["BLAT_TYPE"] = "'-t=dna -q=dna'"

            prepareScript("rblat_univec",
                                        "cleaning/larablat.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        READS_FILES_COUNT * 32, 1, "6:00:00", env)
            slurm_id = prepareAndSubmit("rblat_univec",
                                        "dockers/cleaning/blat.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        READS_FILES_COUNT * 32, 1, "6:00:00", env)

            slurm_ids.append(slurm_id)
            blat_dep.append(slurm_id)


#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
        if "BLAT_ECOLI" in steps:

            env["BLAT_READS_DB"] = BLAST_DB_FOLDER + "E_coli_G/E_coli_G"
            env["BLAT_TYPE"] = "'-t=dna -q=dna'"

            prepareScript("rblat_ecoli",
                                        "cleaning/larablat.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        READS_FILES_COUNT * 32, 1, "6:00:00", env)
            slurm_id = prepareAndSubmit("rblat_ecoli",
                                        "dockers/cleaning/blat.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        READS_FILES_COUNT * 32, 1, "6:00:00", env)

            slurm_ids.append(slurm_id)
            blat_dep.append(slurm_id)

#-------------------------------------------------------------------------------
        if "BLAT_SCERE" in steps:

            env["BLAT_READS_DB"] = BLAST_DB_FOLDER + "S_cerevisiae_G/S_cerevisiae_G"
            env["BLAT_TYPE"] = "'-t=dna -q=dna'"

            prepareScript("rblat_scere",
                                        "cleaning/larablat.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        READS_FILES_COUNT * 32, 1, "6:00:00", env)

            slurm_id = prepareAndSubmit("rblat_scere",
                                        "dockers/cleaning/blat.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        READS_FILES_COUNT * 32, 1, "6:00:00", env)

            slurm_ids.append(slurm_id)

#------------------------------------------------------------------------------
        if "BLAT_CUSTOM_READS" in steps:
            for db in BLATN_CUSTOM_READS:
                env["BLAT_READS_DB"] = DATA_FOLDER + db
                env["BLAT_TYPE"] = "'-t=dna -q=dna'"

                prepareScript("rblat_" + db,
                                            "cleaning/larablat.cmd",
                                            dep,
                                            folders_dict["OUT_FOLDER"],
                                            READS_FILES_COUNT * 32, 1, "6:00:00", env)

                slurm_id = prepareAndSubmit("rblat_" + db,
                                            "dockers/cleaning/blat.cmd",
                                            dep,
                                            folders_dict["OUT_FOLDER"],
                                            READS_FILES_COUNT * 32, 1, "6:00:00", env)

                slurm_ids.append(slurm_id)
                blat_dep.append(slurm_id)


#-------------------------------------------------------------------------------
# CLEANING FROM BLAT HITS:
        prepareScript("blat_parser",
                                    "cleaning/larablat_parser.cmd",
                                    blat_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "2:00:00", env)

        slurm_id = prepareAndSubmit("blat_parser",
                                    "dockers/cleaning/blat_parser.cmd",
                                    blat_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "2:00:00", env)

        slurm_ids.append(slurm_id)
        dep.append(slurm_id)

        slurm_id = prepareAndSubmit("reads_removal",
                                    "cleaning/reads_removal.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 1, "3:00:00", env)

        slurm_ids.append(slurm_id)
        dep.append(slurm_id)

        # Set input for next step:
        env["READS_FILES"] = env["READS_OUT"]
#-------------------------------------------------------------------------------
# Pointing to clean reads files
# If a cleaning has been first performed have to add the CLEANING_FOLDER PATH
if soft_data.cleaning_progs & steps:

    reads_tmp =  env["READS_FILES"].replace("'", "").split()
    env["READS_FILES"] = "'" + " ".join([ folders_dict["CLEANING_FOLDER"] + x
                          for x in reads_tmp ]) + "'"
    print( "'" + " ".join([ folders_dict["CLEANING_FOLDER"] + x
                          for x in reads_tmp ]) + "'")
#-------------------------------------------------------------------------------
if "FASTQC2" in steps:
    prepareScript("fastqc2",
                                "cleaning/larafastqc2.cmd",
                                dep,
                                folders_dict["OUT_FOLDER"],
                                READS_FILES_COUNT, 2, "03:00:00", env,
                                folders_dict["STAT_FOLDER"] + "fastqc2_report")
    
    slurm_id = prepareAndSubmit("fastqc2",
                                "dockers/cleaning/fastqc2.cmd",
                                dep,
                                folders_dict["OUT_FOLDER"],
                                READS_FILES_COUNT, 2, "03:00:00", env,
                                folders_dict["STAT_FOLDER"] + "fastqc2_report")
    slurm_ids.append( slurm_id )
    # Fastqc doesn't have to be incorporated in the dependency list

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# ASSEMBLY
#-------------------------------------------------------------------------------
if soft_data.ass_map_progs & steps:

    os.mkdir(folders_dict["ASSEMBLY_MAPPING_FOLDER"])
   
#-------------------------------------------------------------------------------
    if "TRINITY" in steps:
        
        prepareScript("trinity",
                                    "ass_map/laratrinity.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    2, 16, "72:00:00", env)
        slurm_id = prepareAndSubmit("trinity",
                                    "dockers/ass_map/trinity.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    2, 16, "72:00:00", env)

        slurm_ids.append( slurm_id )
        dep.append(slurm_id)

# Setting the ASSEMBLY_FILE variable
        env["ASSEMBLY_FILE"] = folders_dict["ASSEMBLY_MAPPING_FOLDER"] + "trinity/Trinity.fasta"
        
#-------------------------------------------------------------------------------
    if "CDHITEST" in steps:

        prepareScript("cdhitest",
                                    "ass_map/laraclustering.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env)
        slurm_id = prepareAndSubmit("cdhitest",
                                    "dockers/ass_map/clustering.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env)
        slurm_ids.append( slurm_id )

        dep.append(slurm_id)

        env["ASSEMBLY_FILE"]= folders_dict["ASSEMBLY_MAPPING_FOLDER"] + "cdhitest/assembly_clust.fas"

#-------------------------------------------------------------------------------
    if "ASSEMBLY_QUAL" in steps:
        env["BLAST_QUAL_DB"] = BLAST_DB_FOLDER + "uniprot_qc/uniprot_sprot.fasta"
        prepareScript("qc_blast",
                                    "ass_map/larablast_qc.cmd", dep,
                                    folders_dict["OUT_FOLDER"], 1, 16,
                                    "24:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "assembly_qc/blast_qc")
        slurm_id = prepareAndSubmit("qc_blast",
                                    "dockers/ass_map/blast_qc.cmd", dep,
                                    folders_dict["OUT_FOLDER"], 1, 16,
                                    "24:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "assembly_qc/blast_qc")
        slurm_ids.append( slurm_id )
                                    

        prepareScript("cegma",
                                    "ass_map/laracegma.cmd", dep,
                                    folders_dict["OUT_FOLDER"], 1, 16,
                                    "24:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "assembly_qc/cegma")
        slurm_id = prepareAndSubmit("cegma",
                                    "dockers/ass_map/cegma.cmd", dep,
                                    folders_dict["OUT_FOLDER"], 1, 16,
                                    "24:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "assembly_qc/cegma")

        slurm_ids.append( slurm_id )
        
#-------------------------------------------------------------------------------
    if "BOWTIE1" in steps:

        prepareScript("bowtie1",
                                    "ass_map/larabowtie.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env)
        slurm_id = prepareAndSubmit("bowtie1",
                                    "dockers/ass_map/bowtie.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env)
        slurm_ids.append( slurm_id )

        # TO CHANGE WHEN EXPRESSION INCORPORATED:
        # bowtie isn't in dependency list yet

#-------------------------------------------------------------------------------
    if "HISAT2" in steps:

        prepareScript("hisat2",
                                    "ass_map/larahisat2.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "24:00:00", env)
        slurm_id = prepareAndSubmit("hisat2",
                                    "dockers/ass_map/hisat2.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "24:00:00", env)
        slurm_ids.append( slurm_id )
        expr_dep.append(slurm_id)

        # Bam postprocessing
        prepareScript("bam_postprocess",
                                    "ass_map/larabam_postproc.cmd",
                                    expr_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "24:00:00", env)
        slurm_id = prepareAndSubmit("bam_postprocess",
                                    "dockers/ass_map/bam_postproc.cmd",
                                    expr_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "24:00:00", env)
        slurm_ids.append( slurm_id )
        expr_dep.append(slurm_id)

#-------------------------------------------------------------------------------
# IDENTIFICATION / ANNOTATION         
#-------------------------------------------------------------------------------
print steps
if soft_data.identify_progs & steps:
    # OUTPUT folder:
    os.mkdir(folders_dict["IDENTIFICATION_FOLDER"])

    # If at least one blat search:
    if soft_data.blat_ass_progs & steps:

        #splitting assembly file:
        
        prepareScript("split4cblat",
                                    "identify/larasplitting.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 4, "00:30:00", env)
        slurm_id = prepareAndSubmit("split4cblat",
                                    "dockers/identify/splitting.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 4, "00:30:00", env)
        slurm_ids.append( slurm_id )
        blat_dep.append(slurm_id)

#-------------------------------------------------------------------------------
        if "BLAT_CEGMA" in steps:

            env["BLAT_CONTIGS_DB"] = BLAST_DB_FOLDER + "cegma_euk_prot_core/cegma_euk_prot_core"
            env["BLAT_TYPE"] = "'-t=dnax -q=prot'"

            prepareScript("cblat_cegma",
                                        "identify/larablat.cmd",
                                        blat_dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_id = prepareAndSubmit("cblat_cegma",
                                        "dockers/identify/blat.cmd",
                                        blat_dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_ids.append( slurm_id )
            blat_dep.append(slurm_id)
                            
#-------------------------------------------------------------------------------
        if "BLAT_UNIREF" in steps:

            env["BLAT_CONTIGS_DB"] = BLAST_DB_FOLDER + "uniref90/uniref90"
            env["BLAT_TYPE"] = "'-t=dnax -q=prot'"

            prepareScript("cblat_uniref",
                                        "identify/larablat.cmd",
                                        blat_dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_id = prepareAndSubmit("cblat_uniref",
                                        "dockers/identify/blat.cmd",
                                        blat_dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_ids.append( slurm_id )
            blat_dep.append(slurm_id)
                            
#-------------------------------------------------------------------------------
        if "BLAT_NR" in steps:

            env["BLAT_CONTIGS_DB"] = BLAST_DB_FOLDER + "nr/nr"
            env["BLAT_TYPE"] = "'-t=dnax -q=prot'"


            prepareScript("cblat_nr",
                                        "identify/larablat.cmd",
                                        blat_dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_id = prepareAndSubmit("cblat_nr",
                                        "dockers/identify/blat.cmd",
                                        blat_dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_ids.append( slurm_id )
            blat_dep.append(slurm_id)
                            
#-------------------------------------------------------------------------------
        if "BLAT_CUSTOM_ASS" in steps:
            for db in BLATN_CUSTOM_ASS:
                env["BLAT_CONTIGS_DB"] = folders_dict["DATA_FOLDER"] + db
                env["BLAT_TYPE"] = "'-t=dna -q=dna'"

                prepareScript("cblatn_"+db,
                                            "identify/larablat.cmd",
                                            blat_dep,
                                            folders_dict["OUT_FOLDER"],
                                            64, 1, "72:00:00", env)
                slurm_id = prepareAndSubmit("cblatn_"+db,
                                            "dockers/identify/blat.cmd",
                                            blat_dep,
                                            folders_dict["OUT_FOLDER"],
                                            64, 1, "72:00:00", env)
                slurm_ids.append( slurm_id )
                blat_dep.append(slurm_id)

            for db in BLATX_CUSTOM_ASS:
                env["BLAT_CONTIGS_DB"] = folders_dict["DATA_FOLDER"] + db
                env["BLAT_TYPE"] = "'-t=dnax -q=prot'"

                prepareScript("cblatx_"+db,
                                            "identify/larablat.cmd",
                                            blat_dep,
                                            folders_dict["OUT_FOLDER"],
                                            64, 1, "72:00:00", env)
                slurm_id = prepareAndSubmit("cblatx_"+db,
                                            "dockers/identify/blat.cmd",
                                            blat_dep,
                                            folders_dict["OUT_FOLDER"],
                                            64, 1, "72:00:00", env)
                slurm_ids.append( slurm_id )
                blat_dep.append(slurm_id)

        # Tidying blat outputs
        prepareScript("cleaning_blat",
                                    "identify/laraafter_blat_cleaning.cmd",
                                    blat_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 1, "00:30:00", env)
        slurm_id = prepareAndSubmit("cleaning_blat",
                                    "dockers/identify/after_blat_cleaning.cmd",
                                    blat_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 1, "00:30:00", env)
        slurm_ids.append( slurm_id )
        blat_dep.append(slurm_id)
                
#-------------------------------------------------------------------------------
    # If at least one HMMER search:
    if soft_data.hmmer_ass_progs & steps:
        
        prepareScript("split4hmmer",
                                    "identify/larasplitting_4_hmmer.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 4, "01:00:00", env)
        slurm_id= prepareAndSubmit("split4hmmer",
                                    "dockers/identify/splitting_4_hmmer.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 4, "01:00:00", env)
        slurm_ids.append( slurm_id )
        hmmer_dep.append(slurm_id)

#-------------------------------------------------------------------------------
        if "HMMER_PFAMA" in steps:
            env["HMM_PROFILE"] = "PfamA"
            env["HMM_PATH"] = HMMER_PROFILE_FOLDER

            prepareScript("hmm_scan",
                                        "identify/larahmmer_scan.cmd",
                                        hmmer_dep,
                                        folders_dict["OUT_FOLDER"],
                                        6, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("hmm_scan",
                                        "dockers/identify/hmmer_scan.cmd",
                                        hmmer_dep,
                                        folders_dict["OUT_FOLDER"],
                                        6, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            hmmer_dep.append(slurm_id)
            
#-------------------------------------------------------------------------------
        if "HMMER_PFAMB" in steps:

            env["HMM_PROFILE"] = "PfamB"
            env["HMM_PATH"] = HMMER_PROFILE_FOLDER
            prepareScript("hmm_scan",
                                        "identify/larahmmer_scan.cmd",
                                        hmmer_dep,
                                        folders_dict["OUT_FOLDER"],
                                        6, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("hmm_scan",
                                        "dockers/identify/hmmer_scan.cmd",
                                        hmmer_dep,
                                        folders_dict["OUT_FOLDER"],
                                        6, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            hmmer_dep.append(slurm_id)

#-------------------------------------------------------------------------------
        if "HMMER_CUSTOM" in steps:

            for db in HMMER_CUSTOM_DB:
                env["HMM_PROFILE"] = os.path.basename(db)
                env["HMM_PATH"] = folders_dict["DATA_FOLDER"] + db
                prepareScript("hmm_scan",
                                            "identify/larahmmer_scan_custom.cmd",
                                            hmmer_dep,
                                            folders_dict["OUT_FOLDER"],
                                            6, 16, "72:00:00", env)
                slurm_id = prepareAndSubmit("hmm_scan",
                                            "dockers/identify/hmmer_scan_custom.cmd",
                                            hmmer_dep,
                                            folders_dict["OUT_FOLDER"],
                                            6, 16, "72:00:00", env)
                slurm_ids.append( slurm_id )
                hmmer_dep.append(slurm_id)

        # Tidying hmmer outputs
        prepareScript("cleaning_hmmer",
                                    "identify/laraafter_hmmer_cleaning.cmd",
                                    hmmer_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 1, "00:30:00", env)
        slurm_id = prepareAndSubmit("cleaning_hmmer",
                                    "dockers/identify/after_hmmer_cleaning.cmd",
                                    hmmer_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 1, "00:30:00", env)
        slurm_ids.append( slurm_id )
        hmmer_dep.append(slurm_id)
                
#-------------------------------------------------------------------------------
    if "BLASTPLUS_NR" in steps:

        prepareScript("blastplus_nr",
                                    "identify/larablastplus_par.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    16, 16, "72:00:00", env,
                                    folders_dict["IDENTIFICATION_FOLDER"] +
                                    "blastplus_par")
        slurm_id = prepareAndSubmit("blastplus_nr",
                                    "dockers/identify/blastplus_par.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    16, 16, "72:00:00", env,
                                    folders_dict["IDENTIFICATION_FOLDER"] +
                                    "blastplus_par")
        slurm_ids.append( slurm_id )
        b2go_dep.append(slurm_id)

        prepareScript("merge_xml",
                                    "identify/laramerge_xml.cmd",
                                    b2go_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 8, "01:00:00", env)
        slurm_id = prepareAndSubmit("merge_xml",
                                    "dockers/identify/merge_xml.cmd",
                                    b2go_dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 8, "01:00:00", env)
        slurm_ids.append( slurm_id )
        b2go_dep.append(slurm_id)
        
#-------------------------------------------------------------------------------
    if "INTERPROSCAN" in steps:
            prepareScript("ipscan",
                                        "identify/laraipscan.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_id = prepareAndSubmit("ipscan",
                                        "dockers/identify/ipscan.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        64, 1, "72:00:00", env)
            slurm_ids.append( slurm_id )
            b2go_dep.append(slurm_id)

#-------------------------------------------------------------------------------
    if "BLAST2GO" in steps:

        if "BLASTPLUS_NR" in steps:
            prepareScript("b2go_blastplus",
                                        "identify/larab2go_blastplus.cmd",
                                        b2go_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("b2go_blastplus",
                                        "dockers/identify/b2go_blastplus.cmd",
                                        b2go_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            b2go_dep.append(slurm_id)

        else: # no previous BLAST+ nr search:

            # Do the blast+
            prepareScript("blastplus_nr",
                                        "identify/larablastplus_par.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        16, 16, "72:00:00", env,
                                        folders_dict["IDENTIFICATION_FOLDER"] +
                                        "blastplus_par")
            slurm_id = prepareAndSubmit("blastplus_nr",
                                        "dockers/identify/blastplus_par.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        16, 16, "72:00:00", env,
                                        folders_dict["IDENTIFICATION_FOLDER"] +
                                        "blastplus_par")
            slurm_ids.append( slurm_id )
            b2go_dep.append(slurm_id)
            
            prepareScript("merge_xml",
                                        "identify/laramerge_xml.cmd",
                                        b2go_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 8, "01:00:00", env)
            slurm_id = prepareAndSubmit("merge_xml",
                                        "dockers/identify/merge_xml.cmd",
                                        b2go_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 8, "01:00:00", env)
            slurm_ids.append( slurm_id )
            b2go_dep.append(slurm_id)


            # And finally the B2GO job:
            prepareScript("b2go",
                                        "identify/larab2go_blastplus.cmd",
                                        b2go_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("b2go",
                                        "dockers/identify/b2go_blastplus.cmd",
                                        b2go_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            b2go_dep.append(slurm_id)

#-------------------------------------------------------------------------------
    # Summarize annotations
    annot_dep = dep + blat_dep + hmmer_dep + b2go_dep
    prepareScript("annot_summary",
                                "identify/larasummarize_annot.cmd",
                                annot_dep,
                                folders_dict["OUT_FOLDER"],
                                1, 8, "24:00:00", env)
    slurm_id = prepareAndSubmit("annot_summary",
                                "dockers/identify/summarize_annot.cmd",
                                annot_dep,
                                folders_dict["OUT_FOLDER"],
                                1, 8, "24:00:00", env)
    slurm_ids.append( slurm_id )
#-------------------------------------------------------------------------------



        
#-------------------------------------------------------------------------------
# EXPRESSION:
#-------------------------------------------------------------------------------

# If any programs from the expression part:
if soft_data.expression_progs & steps:

    # OUTPUT folder:
    os.mkdir(folders_dict["EXPRESSION_FOLDER"])

#-------------------------------------------------------------------------------
    if "CUFFDIFF" in steps:

        if "HISAT2" in steps:
            # if bowtie already selected by the user
            prepareScript("cuffdiff",
                                        "expression/laracuffdiff.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("cuffdiff",
                                        "dockers/expression/cuffdiff.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )

        else:
            prepareScript("hisat2",
                                        "ass_map/larahisat2.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("hisat2",
                                        "dockers/ass_map/hisat2.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)

            prepareScript("cuffdiff",
                                        "expression/laracuffdiff.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_id = prepareAndSubmit("cuffdiff",
                                        "dockers/expression/cuffdiff.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )

#-------------------------------------------------------------------------------
    if "CUFFLINKS" in steps:
                
        if "HISAT2" in steps:
            # if bowtie already selected by the user
            prepareScript("cufflinks",
                                        "expression/laracufflinks.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_id = prepareAndSubmit("cufflinks",
                                        "dockers/expression/cufflinks.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append( slurm_id )

        else:
            slurm_id = prepareAndSubmit("hisat2",
                                         "ass_map/hisat2.cmd",
                                         dep,
                                         folders_dict["OUT_FOLDER"],
                                         1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)

            prepareScript("cufflinks",
                                        "expression/laracufflinks.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_id = prepareAndSubmit("cufflinks",
                                        "dockers/expression/cufflinks.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append( slurm_id )
            
#-------------------------------------------------------------------------------
    if "RSEM" in steps:

        prepareScript("RSEM",
                                    "expression/laraRSEM.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "expression_stats")
        slurm_id = prepareAndSubmit("RSEM",
                                    "dockers/expression/RSEM.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "expression_stats")
        slurm_ids.append(slurm_id)

#-------------------------------------------------------------------------------
    if "EXPRESS" in steps:

        if "HISAT2" in steps:
            prepareScript("express",
                                        "expression/laraexpress.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 1, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_id = prepareAndSubmit("express",
                                        "dockers/expression/express.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 1, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append(slurm_id)
        else:
            # Perform bowtie and post processing
            prepareScript("hisat2",
                                        "ass_map/larahisat2.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "24:00:00", env)
            slurm_id = prepareAndSubmit("hisat2",
                                        "dockers/ass_map/hisat2.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "24:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)
            
            # Bam postprocessing
            prepareScript("bam_postprocess",
                                        "ass_map/larabam_postproc.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "24:00:00", env)
            slurm_id = prepareAndSubmit("bam_postprocess",
                                        "dockers/ass_map/bam_postproc.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "24:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)

            prepareScript("express",
                                        "expression/laraexpress.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 1, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_id = prepareAndSubmit("express",
                                        "dockers/expression/express.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 1, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append(slurm_id)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# print list of SLURM IDS:
if not DEBUG:
    print "slurmids: " + ",".join(slurm_ids)
