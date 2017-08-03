#-------------------------------------------------------------------------------
# EXPRESSION:
#-------------------------------------------------------------------------------

# If any programs from the expression part:
if soft_data.expression_progs & steps:

    # OUTPUT folder:
    os.mkdir(folders_dict["EXPRESSION_FOLDER"])

#-------------------------------------------------------------------------------
    if "CUFFDIFF" in steps:

        if "BOWTIE2" in steps:
            # if bowtie already selected by the user
            slurm_id = prepareAndSubmit("cuffdiff",
                                        "expression/cuffdiff.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )

        else:
            slurm_id = prepareAndSubmit("bowtie2",
                                        "ass_map/bowtie2.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)

            slurm_id = prepareAndSubmit("cuffdiff",
                                        "expression/cuffdiff.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )

#-------------------------------------------------------------------------------
    if "CUFFLINKS" in steps:
                
        if "BOWTIE2" in steps:
            # if bowtie already selected by the user
            slurm_id = prepareAndSubmit("cufflinks",
                                        "expression/cufflinks.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append( slurm_id )

        else:
            slurm_id = prepareAndSubmit("bowtie2",
                                         "ass_map/bowtie2.cmd",
                                         dep,
                                         folders_dict["OUT_FOLDER"],
                                         1, 16, "72:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)

            slurm_id = prepareAndSubmit("cufflinks",
                                        "expression/cufflinks.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append( slurm_id )
            
#-------------------------------------------------------------------------------
    if "RSEM" in steps:

        slurm_id = prepareAndSubmit("RSEM",
                                    "expression/RSEM.cmd",
                                    dep,
                                    folders_dict["OUT_FOLDER"],
                                    1, 16, "72:00:00", env,
                                    folders_dict["STAT_FOLDER"] +
                                    "expression_stats")
        slurm_ids.append(slurm_id)

#-------------------------------------------------------------------------------
    if "EXPRESS" in steps:

        if "BOWTIE2" in steps:
            slurm_id = prepareAndSubmit("express",
                                        "expression/express.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 1, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append(slurm_id)
        else:
            # Perform bowtie and post processing
            slurm_id = prepareAndSubmit("bowtie2",
                                        "ass_map/bowtie2.cmd",
                                        dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "24:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)
            
            # Bam postprocessing
            slurm_id = prepareAndSubmit("bam_postprocess",
                                        "ass_map/bam_postproc.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 16, "24:00:00", env)
            slurm_ids.append( slurm_id )
            expr_dep.append(slurm_id)

            slurm_id = prepareAndSubmit("express",
                                        "expression/express.cmd",
                                        expr_dep,
                                        folders_dict["OUT_FOLDER"],
                                        1, 1, "72:00:00", env,
                                        folders_dict["STAT_FOLDER"] +
                                        "expression_stats")
            slurm_ids.append(slurm_id)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
