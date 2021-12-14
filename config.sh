#********************PARAMETERS**********************
COLLECTION_DIR="/vol/local/streptomyces-collection"
SCRIPTS_DIR="/vol/local/streptidy"
GENOME_SIZE="7.5m"
GRAM="pos"
RESSOURCES="/vol/local/ressources"
GENUS="Streptomyces"
MEMORY=16
CPU=16
LOG=$SCRIPTS_DIR"/Streptidy.log"

#********************FUNCTIONS**********************
echolog (){
    DATE_LOG=`date +"%Y %m %d %H:%M:%S"`
    echo -e "$DATE_LOG\t$1" >> $LOG
}