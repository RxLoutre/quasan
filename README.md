# Streptidy

#### 🚧 Work in progress 🚧

Streptidy is a pipeline meant to automatically run itself on the [ILis] (IBL Linux Server). It will watch over the directory containing a in house _streptomyces_  genomes collection, and.. keep it tidy of course 🥁.

Streptidy will start from a directory filled with raw reads, and then make use of the python script **Quasan** (**Qu**ality **As**sembly **An**notation)

## Overview

Here will be some nice pictures soon

## Installation

```bash
#Download using git clone from gitlab repo
git clone https://gitlab.services.universiteitleiden.nl/ibl-bioinformatic/streptidy.git
#If mamba already not in base environment
conda install -n base -c bioconda mamba
#Use the provided yaml file to create the environment easily
mamba env create -f quasan.yml
```

## Usage

```python
#Enlightenment soon to come
```