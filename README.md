# Streptidy

#### 👷🏻‍♀️ Work in progress 🚧

Streptidy is a pipeline meant to automatically run itself on the [ALICE](https://wiki.alice.universiteitleiden.nl/index.php?title=ALICE_User_Documentation_Wiki) cluster. He will watch over the directory containing the MBT collection, a large collection of exotic _Streptomyces_ genomes, and.. keep it tidy of course 🥁.

Streptidy will start from a directory filled with raw reads, and then make use of the python script **Quasan** (**Qu**ality **As**sembly **An**notation)

## Overview

Here will be some nice pictures soon

## Installation

Streptidy is a custom script not meant to be exported.  

However you will be able to install Quasan when it is finished. First you would need to prepare an appropriate conda environment (or maybe I will do that for you, but I don't know for now) : 

```bash
conda create -n quasan
conda activate quasan
#Yep, time for a lot of packages
conda install -c bioconda shovill
conda install -c bioconda quast
conda install -c bioconda fastqc
conda install -c bioconda multiqc
conda install -c bioconda busco
conda install -c bioconda antismash
conda install -c bioconda prokka
conda install -c bioconda bam2fastx
conda install -c bioconda flye
conda install -c bioconda antismash
```

## Usage

```python
#Enlightenment soon to come
```