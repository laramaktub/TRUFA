
#### Make the GFF file:
# This is only working with Trinity now !

#### TO CHANGE:
# cuffdiff need multiple bam files !!!! 

cd $ASSEMBLY_MAPPING_FOLDER

if [ -n "$ASSEMBLY_FILE" ]
then
    transcripts=$ASSEMBLY_FILE

else
    echo "EK: check the cuffdiff code"
fi

gff_file=${OUT_FOLDER}tmp.gff
outfolder=${EXPRESSION_FOLDER}cuffdiff

mkdir $outfolder

time ${PY_BIOLIB_PATH}work_on_assemblies_2.py $transcripts -gff > $gff_file

#-------------------------------------------------------------------------------

time cuffdiff $gff_file \
${ASSEMBLY_MAPPING_FOLDER}bam_output.bam \
-o $outfolder -p 16
