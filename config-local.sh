#********************PARAMETERS**********************
COLLECTION_DIR_LOCAL="/Users/roxaneboyer/Bioinformatic/data/mbt_genomes/mbt-training-collection"
COLLECTION_DIR_REMOTE="RD:IBL_Bioinformatic/Roxane/mbt-genomes/"
SCRIPTS_DIR="/Users/roxaneboyer/Bioinformatic/scripts/streptidy"
GENOME_SIZE="7.5m"
LOG_DIR="/Users/roxaneboyer/Bioinformatic/logs"
GRAM="pos"
RESSOURCES="/Users/roxaneboyer/Bioinformatic/ressources"
GENUS="Streptomyces"
MEMORY=8
CPU=8
LOG=$SCRIPTS_DIR"/Streptidy.log"

#********************FUNCTIONS**********************
echolog (){
    DATE_LOG=`date +"%Y %m %d %H:%M:%S"`
    echo -e "[$1] $DATE_LOG\t$2" >> $LOG
}