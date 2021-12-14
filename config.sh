#********************PARAMETERS**********************
COLLECTION_DIR_LOCAL="/vol/local/streptomyces-collection"
COLLECTION_DIR_REMOTE="RD:IBL_G_Van_Wezel/mbt-genomes/"
SCRIPTS_DIR="/vol/local/streptidy"
GENOME_SIZE="7.5m"
LOG_DIR="/vol/local/logs"
GRAM="pos"
RESSOURCES="/vol/local/ressources"
GENUS="Streptomyces"
MEMORY=16
CPU=16
LOG=$SCRIPTS_DIR"/Streptidy.log"

#********************FUNCTIONS**********************
echolog (){
    DATE_LOG=`date +"%Y %m %d %H:%M:%S"`
    echo -e "[$1] $DATE_LOG\t$2" >> $LOG
}