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
	case "${OPTION}"
	in
	t) TEST=1;;
	s) STRAINS+=("$OPTARG");;
	h) HALF=1;;
    m) MAIL=$OPTARG
	esac
done

#If test mode, then we run in local mode
if (( $TEST==1 ))
then
    source config-local.sh
else
    source config.sh
fi

#Activate conda environement
conda activate quasan

echolog "*******************Streptidy awaken*****************"

for STRAINS in "${STRAIN[@]}"; do
    echolog "Working on strain $STRAIN"
done

#Retrieve all versions informations for all tools

#Run for all the strains he was called for
    #Look for differences
    #If differences between RD and Ilis
        #Upload the new things from RD on Ilis
    #Run
    #Push updated directory in RD with rclone
#Send an email when analysis is done for a certain strain

#Perform a general quast on all assemblies (oof !)

#Maybe later : Perform big_scape