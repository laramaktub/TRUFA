#! /usr/bin/env python

import subprocess
import os
import sys
import soft_data
import config
import mimetypes

# for the default parameters dictionnary
PROG_SET = soft_data.prog_set
PARAM_DICT = soft_data.arguments_dict
print PARAM_DICT
#-------------------------------------------------------------------------------
def get_parameters(REALUSER, para_dict_str):
    """
    STATUS: SEEMS TO WORK, TO DOUBLE CHECK
    This is a really clumsy function to parse the options/parameters from the
    webserver to a python dictionnary on altamira
    """
    
    test = para_dict_str.strip('"')
    test = test.strip("<>")
    test = test.partition(" ")[2]
    test = test.strip("{}")
    test = test.replace(": u'", ":")
    test = test.replace("'", "")
    test = test.split(",")
    
    mydict = dict()
    for item in test:
        item = item.split(":")
        if item[1]: # don't add to dict if no values
            mydict[item[0].strip()] = item[1].strip()
            
    return REALUSER, mydict
    
#-------------------------------------------------------------------------------
def sort_parameters(usr_para_dict):
    """
    STATUS: WORKING
    Sort the parameters of the dictionnary by analysis steps (trimming options
    all together, duplication options all together ...)
    """

    args_dict = {}
    input_dict = {}

    # Special case for the DUP_DEREP parameter:
    derep_keys = [x for x in usr_para_dict if x.startswith("DUP_DEREP")]
    derep_param = ""
    for key in derep_keys:
        if usr_para_dict[key] == "on":
            derep_param += key[-1] # the last character is the number for the opt.
            del usr_para_dict[key]
    usr_para_dict["DUP_FILTER"] = derep_param
    # get type of input and input file(s):
    input_type = usr_para_dict["input_type"]
    input_dict["input_type"] = input_type
    del usr_para_dict["input_type"]

    reads_files = [ usr_para_dict[x]
                    for x in usr_para_dict
                    if x.startswith("file_read")]
    input_dict["reads_files"] = reads_files

    if "file_ass" in usr_para_dict:
        assembly_file = usr_para_dict["file_ass"]
        input_dict["assembly_file"] = assembly_file
    
    # WARNING: DELETE all entrie from dict starting with "file"
    keys_to_del = [ x
         for x in usr_para_dict
         if x.startswith("file") ]
    
    for k in keys_to_del:
        del usr_para_dict[k]

# checking for correct number of input:
    if input_type == "single" and len(reads_files) != 1:
        raise IOError("Input should be single but not 1 readfile as input")
    elif input_type == "paired" and len(reads_files) != 2:
        raise IOError("Input should be paired but not 2 readfile as input")
    elif input_type == "contigs" and "assembly_file" not in input_dict:
        raise IOError("Input should be contigs but cannot find assembly file")
    elif input_type =="contigs_with_single":
        if len(reads_files) != 1:
            raise IOError("Input should be contigs and one single read file but not 1 read file as input")
        if "assembly_file" not in input_dict:
            raise IOError("Input should be contigs and one single assembly file but  cannot find assembly file")
    elif input_type =="contigs_with_paired":
        if len(reads_files) != 2:
            raise IOError("Input should be contigs and two paired read files but not 2 read files as input")
        if "assembly_file" not in input_dict:
            raise IOError("Input should be contigs and two paired reads files but cannot find assembly file")

    # get blat_dbs:
    blat_db_reads_n = [usr_para_dict[x]
                       for x in usr_para_dict
                       if x.startswith("blat_custom_reads_n")]

    blat_db_ass_n = [usr_para_dict[x]
                     for x in usr_para_dict
                     if x.startswith("blat_custom_ass_n")]

    blat_db_ass_aa = [usr_para_dict[x]
                      for x in usr_para_dict
                      if x.startswith("blat_custom_ass_aa")]
    hmm_db = [usr_para_dict[x]
              for x in usr_para_dict
              if x.startswith("hmm_custom")]


    input_dict["blatn_reads"] = blat_db_reads_n
    input_dict["blatn_ass"] = blat_db_ass_n
    input_dict["blatx_ass"] = blat_db_ass_aa
    input_dict["hmm_custom_db"] = hmm_db

    key_to_del = [x for x in usr_para_dict
                  if x.startswith("blat_custom_")
                  or x.startswith("hmm_custom")]
    
    for key in key_to_del:
        del usr_para_dict[key]

    # get active programs:
    progs = set([x for x in usr_para_dict if x in PROG_SET])

    input_dict["progs"] = progs
    for prog in progs:
        del usr_para_dict[prog]
    
    # to add blat steps if blat customs
    if blat_db_reads_n:
        progs.add("BLAT_CUSTOM_READS")
    if blat_db_ass_n or blat_db_ass_aa:
        progs.add("BLAT_CUSTOM_ASS")
    if hmm_db:
        progs.add("HMMER_CUSTOM")

    if len(progs) == 0:
        raise IOError("It seems that not a single program has been selected for the analysis")

    # Specify the customized options for each program
    params = usr_para_dict.keys()
    para_groups = [ x.split("_")[0] for x in params ]   
    para_groups = set(para_groups)
    for param in usr_para_dict:
        for para_group in para_groups:
            if param.startswith(para_group):
                if para_group in args_dict:
                    args_dict[para_group] += PARAM_DICT[param] + " " + usr_para_dict[param] + " "
                else:
                    args_dict[para_group] = PARAM_DICT[param] + " " + usr_para_dict[param] + " "
    # Adding ' ' for bash export:
    for k in args_dict:
        args_dict[k] = "'" + args_dict[k] + "'"
    
    input_dict["args_dict"] = args_dict
    return input_dict
        
#-------------------------------------------------------------------------------
def set_environment(input_dict, folders_dict):
    """
    Setup of the environment variables which will be then exported
    in make_and_submit_job for the BASH scripts
    """
    
    #env = os.environ.copy()
    env = dict()

    env["PIPE_INPUT_TYPE"] = input_dict["input_type"]

    if "reads_files" in input_dict:
        env["READS_FILES"] = "'" + " ".join(input_dict["reads_files"]) + "'"
    if "assembly_file" in input_dict:
        env["ASSEMBLY_FILE"] = input_dict["assembly_file"]

#### Not sure the next "for" loop will be necessary:
    for prog in input_dict["progs"]:
        env["PIPE_" + prog] = "ON"

    for args in input_dict["args_dict"]:
        env["PARAM_" + args] = input_dict["args_dict"][args]

    for folder in folders_dict:
        env[folder] = folders_dict[folder]

    
    return env


#-------------------------------------------------------------------------------



def make_and_submit_job(OUT_FOLDER, cmd_file, job_name,
                        total_tasks, cpus_per_task, wall_clock_limit, dep, env,
                        debug = False):
    """
    Write a command file to a temporary file and submit it to altamira

    STATUS: WORKING
    """
    print(dep)
    import tempfile
    cache_path = OUT_FOLDER + ".cache/"
    #log_path = cache_path + job_name + "%j"
    log_path = OUT_FOLDER + "log/" + job_name + "%j"
    tmp_path = cache_path + "tmp/"
    os.chdir(cache_path)
    # Preparing temporary files for submission:
    fd, cmd_path = tempfile.mkstemp(dir="tmp",prefix=job_name + "_")
    os.chmod(cmd_path, 0644)
    with open(cmd_path, "w") as tmp:
        # Preparing the slurm header
        tmp.write("""\
#!/bin/bash
#@ job_name = {0}
#@ initialdir = .
#@ output = {1}.out
#@ error = {1}.err
#@ total_tasks = {2}
#@ cpus_per_task = {3}
#@ wall_clock_limit = {4}
\n""".format(job_name, log_path, total_tasks, cpus_per_task, wall_clock_limit))
    # Adding the environement:
        tmp.write("#" + "-"*34 + "ENVIRONMENT" + "-"*34 + "\n")
        
        for k, i in env.items(): 
            tmp.write("{0}={1}\n".format(k,i))

        tmp.write("#" + "-"*79 + "\n")

    # Adding the actual job part (from the command file without header):
        with open(cmd_file) as f:
            for line in f:
                tmp.write(line)
    # Submit the job
    job_file = os.path.basename(cmd_path)
    if dep:
        dep_str = "--dependency=afterok:" + ":".join(dep)
    else:
        dep_str = ""

    command = "ssh genorama@altamira1.ifca.es 'cd {0} ; mnsubmit --reservation=master_2017 {1} {2}'".format(tmp_path, dep_str, job_file)
    debug=False
    if debug == True:
        print "DEBUG: " + command

    else:
        print "entra en el else"
        job = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, env=env)
        
        # To get the job ID for dependencies
        out, err = job.communicate()
        job_id = out.split()[3]
        return job_id
    


    
#===========================================================================
# Create the script with the actual commands

def make_script(OUT_FOLDER, cmd_file, job_name,
                        total_tasks, cpus_per_task, wall_clock_limit, dep, env,
                        debug = False):
    
    import tempfile
    cache_path = OUT_FOLDER + ".cache/"
    log_path = OUT_FOLDER + "log/"+ job_name + "%j"
    print("jobname ", job_name)
    tmp_path = cache_path + "tmp/"
    os.chdir(cache_path)
    # Preparing temporary files for submission:
    fd, cmd_path = tempfile.mkstemp(dir="tmp",prefix="script_"+job_name + "_")
    os.chmod(cmd_path, 0644)
    with open(cmd_path, "w") as tmp:

    # Adding the environment:
        tmp.write("#" + "-"*34 + "ENVIRONMENT" + "-"*34 + "\n")
        for k, i in env.items(): 
            tmp.write("{0}={1}\n".format(k,i))
           #print "{0}={1}\n".format(k,i)

        tmp.write("#" + "-"*79 + "\n")

        
    # Adding the actual job part (from the command file without header):
        print "archivo comando   :     " + cmd_file
        with open(cmd_file) as f:
            for line in f:
                tmp.write(line)

        #return debug
    
# Cleaning up, closing and removing tmp:
    os.close(fd)
#    os.remove(cmd_path)


#-------------------------------------------------------------------------------
def make_log(REALUSER, input_dict, log_file):

    with open(log_file, "w") as f:

        # For the date:
        import datetime
        today = datetime.datetime.now()
        today = today.strftime("Date: %Y-%m-%d %H:%M")
        f.write(today + "\n")
        f.write("#" + "-"*79 +"\n" )
        
        # User:
        f.write("The current user is: " + REALUSER + "\n")    
        f.write("#" + "-"*79 +"\n" )

        # Input:
        f.write("List of reads_files files:\n")
        reads_files = input_dict["reads_files"]
        for r_f in reads_files:
            f.write(r_f + "\n")

        f.write("#" + "-"*79 +"\n" )
        f.write("Input type:\n")
        f.write(input_dict["input_type"] + "\n")

        # Steps:
        f.write("#" + "-"*79 +"\n" )
        f.write("List of the steps activated:\n")
        for i in input_dict["progs"]:
            f.write(i + "\n")

        # Options:
        f.write("#" + "-"*79 + "\n" )
        f.write("List of arguments for each steps:\n")
        for i in input_dict["args_dict"]:
            f.write(i + ":\n" + input_dict["args_dict"][i] + "\n")
        f.write("#" + "-"*79 +"\n" )
    
