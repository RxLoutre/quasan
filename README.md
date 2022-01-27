# Quasan
					--------------------------------------------------  
					________                                
					\_____  \  __ _______    ___________    ____    
					 /  / \  \|  |  \__  \  /  ___/\__  \  /    \   
					/   \_/.  \  |  // __ \_\___ \  / __ \|   |  \   
					\_____\ \_/____/(____  /____  >(____  /___|  /   
					       \__>          \/     \/      \/     \/   
					    (*Qu*ality - *As*sembly - *An*alysis )  
					--------------------------------------------------		
A pipeline for : Raw Reads QC -> Assembly -> Annotation -> Assembly QC -> BCG Discovery
## For impatient people

```bash
#When logged on Ilis
conda activate quasan
python3 /vol/local/streptidy/Quasan.py -d "MBT42"
```

## Installation

Quasan is meant to be run on a very particular collection and was thefore not coded to be exportable so much.
It is currently installed on the IBL Linux Server (Ilis), as well as its conda environement "quasan" which it needs to run.

Although, if you need to recreate the same environement, I have saved the essential packages used by Quasan in quasan.yml file.

```bash
#Download using git clone from gitlab repo
git clone https://gitlab.services.universiteitleiden.nl/ibl-bioinformatic/streptidy.git
#If mamba already not in base environment
conda install -n base -c bioconda mamba
#Use the provided yaml file to create the environment easily
mamba env create -f quasan.yml
```

## Pipeline overview 

```bash
#Save of the mermaid code itself in case mermaid starts working again in gitlab
#For now, you can see the rendering of this graph below
graph TD;
    Z[1 MBTXX] --> |rawdata parsing| A[Reads]
    Y[2 MBTXX -ia] --> C
    A[Reads dictionnary] -->|illumina assembly shovill| B(MBTXX_shovill.fasta)
    A --> |FastQC| R
    A -->|pacbio assembly flye| G(MBTXX_flye.fasta)
    A -->|hybrid assembly flye + pilon| H(MBTXX_flye_pilon.fasta)
    B --> C{Latest assembly}
    G --> C{Latest assembly}
    H --> C{Latest assembly}
    C --> |Prokka annotation| D[MBTXX_version_prokka.gbk]
    C --> |PGAP annotation| E[MBTXX_version_PGAP.gbk]
    E --> W{Latest GBK}
    X[3 MBTXX -as] --> W
    W --> Q[Antismash]
    C --> |Busco| R[final_report.html]
    C --> |Quast| R[final_report.html]
    C --> |MultiQC| R[final_report.html]
```

[![](https://mermaid.ink/img/pako:eNqNU11PwjAU_Ss3fdIoJOobDyYMEBIlATUB3Qi5bIU1dO3SdpqF8t8t61Cm0bin9nzltqfbkVgmlHTIRmGewnM_EuC-1_AKxsHzfL6AVusWrML3BA1CjkozsbHQDR8pJnrh5S_htZdDi6G39DxT6yBhsWFSCFRlxVvGeZExgYBa02zFS9CpfHOoheCsylrWQHuN2uB5nefnuXPQtGfh8QS1OcYrJr8C17ykFoZ12mH3M8qm5UqxpGmCC8gZl8LC6MS8rLBGROCPuntAQ7X5DNl7dvgnO_qT7flzTpTcbt0dCSENHi7QQj_0I71RV4UUy7yStDer7aJpHXYnDePgm_EgOLENKtvsOM8wuK9HmYc3x3JR-3JnnplVm2nYFYbpDHXanCAodCxdR-Ha9cyXiuZSmXZqMt7UTQt3pf_QjQtuWNX6L0pySTKqMmSJe9C7AxIRk9KMRqTjlgmqbUQisXe6InfvmQ4SZqQinTVyTS8JFkY-lSImHaMKehT1GbqfI6tV-w-8Awov)](https://mermaid.live/edit#pako:eNqNU11PwjAU_Ss3fdIoJOobDyYMEBIlATUB3Qi5bIU1dO3SdpqF8t8t61Cm0bin9nzltqfbkVgmlHTIRmGewnM_EuC-1_AKxsHzfL6AVusWrML3BA1CjkozsbHQDR8pJnrh5S_htZdDi6G39DxT6yBhsWFSCFRlxVvGeZExgYBa02zFS9CpfHOoheCsylrWQHuN2uB5nefnuXPQtGfh8QS1OcYrJr8C17ykFoZ12mH3M8qm5UqxpGmCC8gZl8LC6MS8rLBGROCPuntAQ7X5DNl7dvgnO_qT7flzTpTcbt0dCSENHi7QQj_0I71RV4UUy7yStDer7aJpHXYnDePgm_EgOLENKtvsOM8wuK9HmYc3x3JR-3JnnplVm2nYFYbpDHXanCAodCxdR-Ha9cyXiuZSmXZqMt7UTQt3pf_QjQtuWNX6L0pySTKqMmSJe9C7AxIRk9KMRqTjlgmqbUQisXe6InfvmQ4SZqQinTVyTS8JFkY-lSImHaMKehT1GbqfI6tV-w-8Awov)

## Prerequisites

<a href="https://ibb.co/Y03KGxk"><img src="https://i.ibb.co/mNGY73q/Screenshot-2022-01-26-at-10-49-59.png" alt="Screenshot-2022-01-26-at-10-49-59" border="0"></a><br /><a target='_blank' href='https://nl.imgbb.com/'></a><br />


## Usage

Quasan can be called in 3 differents ways : 
1 : 
2 : 
3 : 

```python
#QC + Assembly + Annotation + BCG Discovery

#Annotation + BCG Discovery

#BGC Discovery

#Smart mode

#Almighty god mode

```

