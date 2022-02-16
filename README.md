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
<p align=center>A pipeline designed for analyzing and keeping tidy a collection of Streptomyces genomes.</p>

## For impatient people

```bash
#When logged on Ilis, activate quasan environement and go to the right location
conda activate quasan
cd /vol/local
#Example 1 : The classic ; Complete analysis of MBT42 (new collection)
python3 streptidy/Quasan.py -s "MBT42"
#Example 2 : Complete analysis of p62 (old collection) with 20 threads
python3 streptidy/Quasan.py -s "p62" -t 20 -d "/vol/local/2-MBT-old-collection"
#Example 3 : Starting the analysis from the annotation steps
#(most recent .fasta in the assembly folder will be used)
python3 streptidy/Quasan.py -s "MBT27" -ia
#Example 4 : Starting the analysis from the anotation step using pgap instead of prokka
python3 streptidy/Quasan.py -s "MBT27" -ia --pgap
#Example 5 : Starting the analysis only from BCG discovery step
#(if new antismash version is avalable for example, most recent .gbk in the annotation folder will be used)
python3 streptidy/Quasan.py -s "MBT42" -as
#Example 6 : Trickster god mode ; Using all possible options and hoping for the best
#(Work best if you are tired of studying Streptomyces and if you want to watch the world burn in blue flammes)
python3 streptidy/Quasan.py -s "SPIRO666" --pgap -b "spirochaetes_odb10" -ia -t 32 -g "neg" -m 32 -e "10.5m" -ge "Spirochaetes"
```

You read a few examples but still have some questions ? The you should definitely read some more of this README :duck: .  

## Options and default parameters

```bash
Mandatory arguments:
    -s  Specify the strain.
        
Options:
    -as  Start the pipeline only from the BCG Discovery step using the latest .gbk file in MBTXX/annotation/pgap directory
	-ia  Start the pipeline only from the Annotation step, using the latest assembly file found in MBTXX/assembly directory
	-b   The busco lineage to calculate genome completeness against (default : streptomycetales_odb10)
	-r   The ressources folder where to download busco information (default : "/vol/local/ressources", when ran on ILis)
	-t   The number of threads to give to external tools (default : 8)
	-m   The maximum amount of memory to be allocated (default : 16Gb)
	-e   The estimated genome size of your strain. (default : 7.5 Mbases)
	-g   The gram type of the bacteria (pos/neg). (default : pos )
	-ge  The genus of the bacteria. (default : Streptomyces)
	--pgap       The annotation process must be ran using PGAP (/!\ It is buggy with genomes with too many contigs)
	--bioproject If annotation must be submitted to the NCBI, use this option to mention the correct bioproject (default : PRJNA9999999)
	--biosample  If annotation must be submitted to the NCBI, use this option to mention the correct biosample (default : SAMN99999999)
	--locustag   If annotation must be submitted to the NCBI, use this option to mention the correct locus_tag (default : TMLOC).
	--debug		 Debug mode to print more informations in the log
```



## Installation

Quasan is meant to be run on a very particular collection and was thefore not designed to be exportable.
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

Quasan is a pipeline that take as input raw reads from genomic DNA, from either Illumina or PacBio technologies. It expects a certain folder structure in order for it to work. In return, he will perform the following steps : Quality Check (Illumina only), Assembly, Assembly QC, Annotation, BCG Discovery. Quasan will produce his output in a structured way, keeping only essentials files and removing intermediary data. For more information about the expected structure, see chapter about Prerequisites.  


Quasan can be called in 3 differents ways : 
1. Like example 1 and 2, you start from the begining and perform the assembly and all the following steps.
2. Like example 3, 4 and 6, (-ia option, Input Assembly) you only start from the annotation step. This allow you to squeeze in a custom assembly you have made on the side with custom tools and parameters.
3. Like example 5, you only start from the BCG discovery step. This allow you to pass on a custom .gbk file you might have produced with a tool of your choice. 

For mode 2 and 3, quasan will look after the most recent file in their respective directory (**most recent .fasta** in assembly folder for -ia mode, **most recent .gbk file** in annotation folder for -as mode. If you use --pgap, then place your gbk in **annotation/pgap** folder. Otherwise place it in **annotation/prokka** folder).  

<details>
    <summary>Saved mermaid code</summary>
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
    D --> W{Latest GBK}
    E --> W{Latest GBK}
    X[3 MBTXX -as] --> W
    W --> Q[Antismash]
    C --> |Busco| R[final_report.html]
    C --> |Quast| R[final_report.html]
    C --> |MultiQC| R[final_report.html]
```
</details>

[![](https://mermaid.ink/img/pako:eNqNU21PwjAQ_iuXftIoJOo3TEwYICZqImgCuhFybIU1bO3SdpiF8t_t1qHMF-I-tc9brne3LQlFREmHrCRmMbz0rwMO9nvzL-DRe5lOZ9Bq3YCR-B6hRshQKsZXBrr-mGKkZk7-6l86ObQYOkvPMbUOIhZqJjhHWVS8YUmSp4wjoFI0XSQFqFhsLGrAO6my5jXQXqLSeFrnuXpuLTTqGRgfoCbDcMHEV-AyKaiBYZ1W3n5GmbhYSBY1TXAGGUsEN3B3YJ5XWCPCc0_dPqCmSn-G7Bw7PMreHWV77p1PUqzXtkecC41lAw30fVfShtpRCD7PKkl7tVjPmtZh96lhHHwzloIDW7-yTfb1DL37upTBX8TUv9pPHZWb-sQxk-oy8rtcM5WiipulebkKhR2ev7QLkMwlzYTU7VinSVM3ym2v_6F7zBPNqnX4RUnOSUpliiyya74tfQHRMU1pQDr2GKFcByTgO6vLM7vkdBAxLSTpaJnTc4K5Fs8FD_d3p-kztH9M6sDdB2qhD-A)](https://mermaid.live/edit/#pako:eNqNU21PwjAQ_iuXftIoJOo3TEwYICZqImgCuhFybIU1bO3SdpiF8t_t1qHMF-I-tc9brne3LQlFREmHrCRmMbz0rwMO9nvzL-DRe5lOZ9Bq3YCR-B6hRshQKsZXBrr-mGKkZk7-6l86ObQYOkvPMbUOIhZqJjhHWVS8YUmSp4wjoFI0XSQFqFhsLGrAO6my5jXQXqLSeFrnuXpuLTTqGRgfoCbDcMHEV-AyKaiBYZ1W3n5GmbhYSBY1TXAGGUsEN3B3YJ5XWCPCc0_dPqCmSn-G7Bw7PMreHWV77p1PUqzXtkecC41lAw30fVfShtpRCD7PKkl7tVjPmtZh96lhHHwzloIDW7-yTfb1DL37upTBX8TUv9pPHZWb-sQxk-oy8rtcM5WiipulebkKhR2ev7QLkMwlzYTU7VinSVM3ym2v_6F7zBPNqnX4RUnOSUpliiyya74tfQHRMU1pQDr2GKFcByTgO6vLM7vkdBAxLSTpaJnTc4K5Fs8FD_d3p-kztH9M6sDdB2qhD-A)


## Prerequisites

<a href="https://ibb.co/Y03KGxk"><img src="https://i.ibb.co/mNGY73q/Screenshot-2022-01-26-at-10-49-59.png" alt="Screenshot-2022-01-26-at-10-49-59" border="0"></a><br /><a target='_blank' href='https://nl.imgbb.com/'></a><br />




```python
#QC + Assembly + Annotation + BCG Discovery

#Annotation + BCG Discovery

#BGC Discovery

#Smart mode

#Almighty god mode

```

