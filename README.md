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

Quasan is a pipeline that take as input raw reads from genomic DNA, from either Illumina or PacBio technologies. It expects a certain folder structure in order for it to work. In return, he will perform the following steps : Quality Check (Illumina only), Assembly, Annotation, BCG Discovery. Quasan will produce his output in a structued way, keeping only essentials files and removing intermediary data. For more information about the expected structure, see [Prerequisites](#Prerequisites).  

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

