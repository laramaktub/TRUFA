#! /bin/bash

extract () {
if [  -f $1 ] ; then
    case $1 in
     *.tar.bz2) tar xvjf $1 ;;
     *.tar.gz) tar xvzf $1 ;;
     *.bz2) bunzip2 $1 ;;
     *.rar) rar x $1 ;;
     *.gz) gunzip $1 ;;
     *.tar) tar xvf $1 ;;
     *.tbz2) tar xvjf $1 ;;
     *.tgz) tar xvzf $1 ;;
     *.zip) unzip $1 ;;
     *.Z) uncompress $1 ;;
     *.7z) 7z x $1 ;;
    *) echo "don't know how to extract '$1'..." ;;
   esac
else
   echo "'$1' is not a valid file!"
fi
}


cd $DATA_FOLDER

for raw in $FILES_TO_UNZIP
do
    raw=`basename $raw`
    r=${raw%.gz}
    r=${r%.tar}
    echo Checking $raw

    if [ -f ${r}*.extracting4alta ]
    then
    	echo Extraction in progress need to wait for $raw
	
	while true
	do
	    sleep 60
	    if [ ! -f ${r}*.extracting4alta ]
	    then
		echo Using already extracted file $r
		break
	    fi
	done

    elif [ -f $r ]
    then
     	echo Using already extracted file $r
    else
 	echo Extracting $raw 
	touch ${raw}.extracting4alta
	extract $raw
	echo Extraction of $raw DONE
	rm ${raw}.extracting4alta
    fi

done