#!/bin/bash

#**********************STREPTIDY************************
# A wrapper of Quasan, meant to keep a collection
# of streptomyces genomes up to date and structured
#
# Will loop on every folder that contains strains data.
# The minimal structure of each dir must be like this :
#        STRAINXX
#         └── raw-reads
#             ├── illumina
#             ├── (pacbio)
#             └── (nanopore)
#
# After running, the structure will look like this :
#        STRAINXX
#         ├── raw-reads
#         │   ├── illumina
#         │   ├── QC
#         │   │   └── multiqc
#         │   ├── illumina
#         │   ├── (pacbio)
#         │   └── (nanopore)
#         ├── assembly
#         │   ├── shovill
#         │   │    └── QC
#         │   └── (hybrid)
#         ├── antismash
#         └── big-scape
#
# Will perform a general quast on all assemblies and
# store the results in the "Resume" folder at the root 
#*******************************************************

source /Users/roxaneboyer/Bioinformatic/scripts/config.sh

