#! /usr/bin/python

# Dictionnary of the arguments keywords for programs from the pipeline
# in arguments dict, BOW2 options are "" check if correct


prog_set = set(["FASTQC1","DUP","TRIM","CUTADAPT","BLAT_UNIVEC","BLAT_ECOLI","BLAT_SCERE","BLAT_CUSTOM_READS", "FASTQC2","TRINITY","ASSEMBLY_QUAL","CDHITEST","BOWTIE1","BLAT_CEGMA","BLAT_UNIREF","BLAT_NR","BLAT_CUSTOM_ASS","HMMER_CEGMA","HMMER_PFAMA","HMMER_PFAMB","HMMER_CUSTOM","BLAST_NR","BLASTPLUS_NR","BLAST2GO","INTERPROSCAN", "BOWTIE2","CUFFDIFF","CUFFLINKS","RSEM","EXPRESS"])

cleaning_progs = set(["DUP", "TRIM","CUTADAPT","BLAT_ECOLI","BLAT_SCERE","BLAT_UNIVEC","BLAT_CUSTOM_READS"])
ass_map_progs = set(["TRINITY","ASSEMBLY_QUAL","CDHITEST","BOWTIE1","BOWTIE2"])
identify_progs = set(["BLAT_CEGMA","BLAT_UNIREF","BLAT_NR","BLAT_CUSTOM_ASS","HMMER_CEGMA","HMMER_PFAMA","HMMER_PFAMB","HMMER_CUSTOM","BLAST_NR","BLASTPLUS_NR","BLAST2GO","INTERPROSCAN"])
expression_progs = set(["CUFFDIFF","CUFFLINKS","RSEM","EXPRESS"])

blat_reads_progs = set(["BLAT_UNIVEC","BLAT_ECOLI","BLAT_SCERE","BLAT_CUSTOM_READS"])
blat_ass_progs = set(["BLAT_CEGMA","BLAT_UNIREF","BLAT_NR","BLAT_CUSTOM_ASS"])
hmmer_ass_progs = set(["HMMER_CEGMA","HMMER_PFAMA","HMMER_PFAMB","HMMER_CUSTOM"])



arguments_dict = dict(DUP_FILTER = "-derep",
                      DUP_NUM = "-derep_min",
                      TRIM_QUAL_THRE = "-min_qual_score",
                      TRIM_MIN_LGTH = "-min_len",
                      TRIM_MAX_LGTH = "-max_len",
                      TRIM_MIN_MEAN_QUAL = "-min_qual_mean",
                      TRIM_QUAL_5 = "-trim_qual_left",
                      TRIM_QUAL_3 = "-trim_qual_right",
                      TRIM_QUAL_WIN = "-trim_qual_window",
                      TRIM_QUAL_STEP = "-trim_qual_step",
                      TRIM_TAIL_5 = "-trim_tail_left",
                      TRIM_TAIL_3 = "-trim_tail_right",
                      TRIM_5_BP = "-trim_left",
                      TRIM_3_BP = "-trim_right",
                      TRIM_CPLEX_MET = "-lc_method",
                      TRIM_CPLEX_THRE = "-lc_threshold",
                      TRIM_PHRED64 = "-phred64",
                      CUTADAPT_ADAPT1 = "-b",
                      CUTADAPT_ADAPT2 = "-b",
                      BLAT_TILE = "-tileSize",
                      BLAT_STEP = "-stepSize",
                      BLAT_ONE_OFF = "-oneOff",
                      BLAT_MIN_MATCH = "-minMatch", 
                      BLAT_MIN_ID = "-minIdentity",
                      BLAT_MIN_SCORE = "-minScore",
                      BLAT_MAX_GAP = "-maxGap",
                      XBLAT_TILE = "-tileSize",
                      XBLAT_STEP = "-stepSize",
                      XBLAT_ONE_OFF = "-oneOff",
                      XBLAT_MIN_MATCH = "-minMatch", 
                      XBLAT_MIN_ID = "-minIdentity",
                      XBLAT_MIN_SCORE = "-minScore",
                      XBLAT_MAX_GAP = "-maxGap",
                      TRIN_SS_LIB = "--SS_lib_type",
                      TRIN_MIN_LGTH = "--min_contig_length",
                      TRIN_JAC_CLIP = "--jaccard_clip",
                      TRIN_MIN_KMER_COV = "--min_kmer_cov",
                      TRIN_MIN_GLUE = "--min_glue",
                      TRIN_MIN_ISO = "--min_iso_ratio",
                      TRIN_GLUE_FACT = "--glue_factor",
                      TRIN_GRP_DIST = "--group_pairs_distance",
                      TRIN_REINF_DIST = "--path_reinforcement_distance",
                      CDHITEST_IDT = "-c",
                      BOW1_MAX_MIS = "-n",
                      BOW1_MAX_SUM = "-e",
                      BOW1_SEED_LGTH = "-l",
                      BOW1_NO_MAQ = "--nomaqround",
                      BOW1_MIN_INS = "-I",
                      BOW1_MAX_INS = "-X",
                      BOW1_MATES_ALI = "",
                      BOW1_TRY_HARD = "-y",
                      BOW2_MODE = "",
                      BOW2_SPEED = "",
                      BOW2_MININS = "--minins",
                      BOW2_MAXINS = "--maxins",
                      BLAST_E_VAL = "-e",
                      BLAST_MAX_TARGET = "-K",
                      BLAST_WORD_SZ = "-W",
                      BLAST_GAP_COST = "-G",
                      BLAST_EXT_COST = "-E",
                      BLAST_REWARD = "-r",
                      BLAST_PENALTY = "-q",
                      XBLAST_E_VAL = "-e",
                      XBLAST_MAX_TARGET = "-K",
                      XBLAST_WORD_SZ = "-W",
                      XBLAST_GAP_COST = "-G",
                      XBLAST_EXT_COST = "-E",
                      # PARAMS EXPRESS
                      EXPR_FRAG_LEN_MEAN = '-m',
                      EXPR_FRAG_LEN_SD = '-s',
                      EXPR_FR_STRD = '',
                      EXPR_RF_STRD = '',
                      EXPR_F_STRD = '',
                      EXPR_R_STRD = '',
                      EXPR_LIB_SIZE = '--library-size',
                      EXPR_MAX_INDEL = '--max-indel-size',
                      EXPR_CALC_COV = '',
)

# Dictionnary with the default parameters values for all programs
# Not sure this is still necessary (to check) default values are (again, I think ...) defined with the html default form

param_dict = {'PARAM_BLAST': '-G 5 -e 1e-5 -q -3 -r 1 -K 15 -W 11 -E 2 ',
              'PARAM_TRIM': '-trim_left 10 -trim_qual_step 1 -trim_qual_right 30 -trim_qual_window 1 -lc_method dust -lc_threshold 32 -trim_tail_right 6 -min_qual_mean 20 -min_len 40 ',
              'PARAM_BLATX': '-stepSize=5 -tileSize=5 -minIdentity=25 -maxGap=2 -minMatch=1 -oneOff=0 -minScore=30 ',
              'PARAM_BLASTX': '-K 15 -W 3 -e 1e-5 -E 1 -G 11 ',
              'PARAM_TRINITY': '--min_iso_ratio 0.05 --min_glue 2  --path_reinforcement_distance 75 --group_pairs_distance 500 --glue_factor 0.05 --min_kmer_cov 1 --min_contig_length 200 ',
              'PARAM_DUP': '-derep_min 2 -derep 1 ',
              'PARAM_BLAT': '-stepSize=11 -oneOff=0 -minIdentity=90 -minMatch=2 -maxGap=2 -minScore=30 -tileSize=11 ',
              'PARAM_BOWTIE': '-n 2 -X 250 -I 0 -e 70 -l 28  --fr '}
