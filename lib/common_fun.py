#! /usr/bin/env python

import sys
import gzip
import tarfile
import re

#-------------------------------------------------------------------------------
def file_to_list(infile):
    """ From a file with contigs names (1 per line), create a python list
    WORKING, TESTING
    """
    contig_list = []
    
    with open(infile,"r") as f:
        for line in f:
            contig_id = line.strip()
            contig_list.append(contig_id)

    contig_list.sort()
   
    return contig_list

#-------------------------------------------------------------------------------
def binary_search(db,query,lo=0,hi=None):
    """
    Perform a binary search:
    STATUS: WORKING

    USAGE:
    if binary_search(id_list, id_to_look_up):
    print id_to_look_up is in id_list 
    """
    
    if hi is None:
        hi = len(db)
    while lo < hi:
        mid = (lo + hi)//2
        midval = db[mid]
        if midval < query:
            lo = mid + 1
        elif midval > query:
            hi = mid
        else:
            return True
    return False

#-------------------------------------------------------------------------------
def check_if_fq(f, n):
    # f the file to check
    # n the number of entries (group of 4 lines, ie: 1 read) to check
    
    # to verify the re expression for the qual line
    
    #define pattern for each lines
    patl1 = re.compile("^@.+")
    patl2 = re.compile("^[NATGCnatgcUWSMKRYBDHVuwsmkrybdhv]+$")
    patl3 = re.compile("^\+.*$")
    qual_chr = re.escape("!#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~}])")
    qual_chr += "\\'"
    qual_chr += '\\"'
    patl4 = re.compile('^[%s]*$'%qual_chr)

    # get group of 4 first lines of fastq
    read_n = 0
    for i in xrange(n):
        read_n += 1
        sid = f.next()
        seq = f.next()
        sid_b = f.next()
        qual = f.next()
        if not patl1.match(sid):
            raise IOError("In file: %s" % f.name
                          + " the read #%d ID line" % read_n
                          + " does not start with '@' or"
                          + " does not have an ID after the '@'.\n"
                          + "Are you sure this is fastq formated file ?\n"
                          + "This is the line containing the error "
                          + "(l%d):\n" % ((read_n - 1)*4 + 1)
                          + sid )

        elif not patl2.match(seq):
            raise IOError("In file: %s" % f.name
                          + " the read #%d sequence line" % read_n
                          + " have invalid nucleotid characters\n"
                          + "Are you sure this is fastq formated file ?\n"
                          + "This is the line containing the error "
                          + "(l%d):\n" % ((read_n - 1)*4 + 2)
                          + seq )
            
        elif not patl3.match(sid_b):
            raise IOError("In file: %s" % f.name
                          + " the read #%d third line" % read_n
                          + " does not start with '+'\n"
                          + "Are you sure this is fastq formated file ?\n"
                          + "This is the line containing the error "
                          + "(l%d):\n" % ((read_n - 1)*4 + 3)
                          + sid_b )
                
        elif not patl4.match(qual):
            raise IOError("In file: %s" % f.name
                          + " the read #%d quality line" % read_n
                          + " does not seem to be encoded quality values.\n"
                          + "Are you sure this is fastq formated file ?\n"
                          + "This is the line containing the error "
                          + "(l%d):\n" % ((read_n - 1)*4 + 4)
                          + qual )

        elif len(seq) != len(qual):
            raise IOError( "In file: %s" % f.name
                           + " the sequence and quality lines"
                           + " of the read #%d" % read_n
                           + " are not of the same length:\n"
                           + "Seq : " + seq 
                           + "Qual: " + qual)
        
    print "GOOD: The following file seems to be a correct fastq file:\n%s" % f.name

#-------------------------------------------------------------------------------
def check_if_fasta(f,n):
    # NOT WORKING AT ALL !
    
    # f the file to check
    # n the number of entries (here sequences) to check

    pat1 = re.compile("^>.+$")
    pat2 = re.compile("^[NATGCnatgcUWSMKRYBDHVuwsmkrybdhv]+$")
    
    flag = "sid"
    
    for l, line in enumerate(f,1):

        print flag
        print line
        
        if flag == "sid":
            if not pat1.match(line):
                raise IOError( "The sequence id line is not correctly formated "
                               + "at line %d:\n" % l
                               + line )
            else:
                flag = "seq"
                seq_l = 0 # number of lines of sequences
                continue

        elif flag == "seq":

            if pat2.match(line):
                seq_l += 1
                continue

            elif line.startswith(">"):
                if seq_l == 0:
                    raise IOError("The sequence in line %d is empty" % (l-1) )
                
                if not pat1.match(line):
                    raise IOError( "The sequence id line is not "
                                   + "correctly formated at line %d:\n" % l
                                   + line )
                else:
                    continue
                
            else:
                raise IOError( "This is not a correct fasta file. "
                               +"Some unrecognized character "
                               + "or an empty line has been found "
                               + "line %d:\n" % l
                               + line )

    print "GOOD: The following file seems to be a correct fasta file:\n%s" % f.name

#-------------------------------------------------------------------------------
def check_inputs_format(input_dict):
# TAR.GZ FILES ARE NOT YET SUPPORTED !
# SUPPOSE THAT GZ FILES ARE ALL FASTQs !!!!

    for key in input_dict:
        if key.startswith("file_read"):
            
            if input_dict[key].endswith(".tar.gz"):
                raise IOError("Don't know how to verify .tar.gz files so far")

            # the following will check the first 10 reads of the fastq files
            elif input_dict[key].endswith(".gz"):
                with gzip.open(input_dict[ key ], 'rb') as f:
                    check_if_fq(f,10000)

            elif input_dict[key].endswith((".fq",".fastq")):
                with open(input_dict[ key ], 'rb') as f:
                    check_if_fq(f,10000)

            else:
                raise IOError("The file %s uploaded as read file " %input_dict[key]
                              + "does not have the correct extension "
                              + "(either fastq or compressed fastq extension)")

        if key.startswith("file_ass"):

            if input_dict[key].endswith((".fa",".fas",".fasta")):
                with open(input_dict[ key ], 'rb') as f:
                    check_if_fasta(f,10)
                
    sys.exit()





    