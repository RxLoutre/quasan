#********************PARAMETERS**********************
COLLECTION_DIR="/Users/roxaneboyer/Bioinformatic/data/mbt_genomes/mbt-training-collection"
SCRIPTS_DIR="/Users/roxaneboyer/Bioinformatic/scripts/streptidy"
GENOME_SIZE="7.5m"
GRAM="pos"
RESSOURCES="/Users/roxaneboyer/Bioinformatic/ressources"
GENUS="Streptomyces"
MEMORY=8
CPU=8
LOG=$SCRIPTD_DIR"/Streptidy.log"

#********************FUNCTIONS**********************
echolog (){
    DATE_LOG=`date +"%Y %m %d %H:%M:%S"`
    echo -e "$DATE_LOG\t$1" >> $LOG
}