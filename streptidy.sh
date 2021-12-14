#!/bin/bash
#**********************STREPTIDY************************
# A wrapper of Quasan, meant to keep a collection
# of streptomyces genomes up to date and structured
#Is called with one or more strain to analyze, for all
#the pipeline or just antismash
#*******************************************************
#Default
TEST=0
MAIL="r.e.boyer@biology.leidenuniv.nl"
#Parse options, strains can accept multiples string as an argument sperated by spaces
while getopts ts:hm: OPTION
do
	case $OPTION
	in
	t) TEST=1;;
	s) STRAINS+=("$OPTARG");;
	h) HALF=1;;
    m) MAIL=$OPTARG
	esac
done
shift $((OPTIND -1))

#If test mode, then we run in local mode
if (( $TEST == 1 ))
then
    source config-local.sh
else
    source config.sh
fi

echolog "streptidy" "*******************Streptidy awaken*****************"

#Retrieve all versions informations for all important tools
ENV_INFO=$(conda list)
ANTISMASH_VERSION=$(echo -e $ENV_INFO | grep "antismash" | tr -s " " | cut -d' ' -f2)
FLYE_VERSION=$(echo -e $ENV_INFO | grep "flye" | tr -s " " | cut -d' ' -f2)
echolog "streptidy" "Important versions to note :"
echolog "streptidy" "ANTISMASH : $ANTISMASH_VERSION"
echolog "streptidy" "FLYE : $FLYE_VERSION"
echolog "streptidy" "*****************************************************"

#Run for all the strains he was called for
for STRAIN in "${STRAINS[@]}"; do
    echolog "streptidy" "-- Working on requested strain $STRAIN"
    #Verify this strain exist
    SOURCE=$COLLECTION_DIR_LOCAL"/"$STRAIN
    DESTINATION=$COLLECTION_DIR_REMOTE"/"$STRAIN
    
    RCLONE_LOG=$LOG_DIR"/"$STRAIN"_rclone.log"
    echolog "streptidy" "-- Checking differences between local collection and remote collection (RD)"
    rclone check --log-file $RCLONE_LOG $SOURCE $DESTINATION
    
done


    #Look for differences
    #If differences between RD and Ilis
        #Upload the new things from RD on Ilis
    #Run
    #Push updated directory in RD with rclone
#Send an email when analysis is done for a certain strain

#Perform a general quast on all assemblies (oof !)

#Maybe later : Perform big_scape