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

## Quick start

```bash
#When logged on Ilis, activate quasan environement and go to the right location
conda activate quasan
cd /vol/local
#Example 1 : The classic ; Complete analysis (Raw reads - QC - Assembly - Annotation - BCG Discovery) of MBT42 (new collection)
python3 streptidy/Quasan.py -s "MBT42"
#Example 2 : Complete analysis of p62 (old collection) with 20 threads
python3 streptidy/Quasan.py -s "p62" -t 20 -d "/vol/local/2-MBT-old-collection"
#Example 3 : Starting the analysis from the annotation steps
#(most recent .fasta in the assembly folder will be used)
python3 streptidy/Quasan.py -s "MBT27" -ia
#Example 4 : Starting the analysis from the anotation step using pgap instead of prokka
python3 streptidy/Quasan.py -s "MBT27" -ia --pgap
#Example 5 : Starting the analysis only from BCG discovery step
#(if new antismash version is avalable for example, most recent .gbk in the pgap annotation folder will be used)
python3 streptidy/Quasan.py -s "MBT42" -as --pgap
#Example 6 : Trickster god mode ; Using all possible options and hoping for the best
#(Work best if you are tired of studying Streptomyces and if you want to watch the world burn in blue flammes)
python3 streptidy/Quasan.py -s "SPIRO666" --pgap -b "spirochaetes_odb10" -ia -t 32 -g "neg" -m 32 -e "10.5m" -ge "Spirochaetes"
```

You read a few examples but still have some questions ? Then you should definitely read some more of this README :duck: .  

## Options and default parameters

```bash
Mandatory arguments:
 -s          Specify the strain you want to analyze, or the folder name where the data is stored
        
Options:
-as          Start the pipeline only from the BCG Discovery step using the latest .gbk file in prokka subfolder (or pgap subfolder if you use the --pgap option)
-ia          Start the pipeline only from the Annotation step, using the latest assembly file found in MBTXX/assembly directory
-b           The busco lineage to calculate genome completeness against (default : streptomycetales_odb10)
-r           The ressources folder where to download busco information (default : "/vol/local/ressources", when ran on ILis)
-t           The number of threads to give to external tools (default : 8)
-m           The maximum amount of memory to be allocated (default : 16Gb)
-e           The estimated genome size of your strain. (default : 7.5 Mbases)
-g           The gram type of the bacteria (pos/neg). (default : pos )
-ge          The genus of the bacteria. (default : Streptomyces)
--pgap       The annotation process must be ran using PGAP (/!\ It does not work with genomes with too many contigs)
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

An option allows Quasan to use PGAP as an annotation tool. PGAP was installed on Ilis by @Du and you can obtain more informations about the process here :  [PGAP HowTo by Du](https://gitlab.services.universiteitleiden.nl/duc/howtos/-/blob/master/Annotate%20genome%20for%20NCBI%20with%20PGAP.md "Thanks Du !"). In big words, I added singularity in quasan conda env for it to be able to call PGAP. The PGAP script we use was also slighlty modified by Du.

## Pipeline overview 

Quasan is a pipeline that take as input raw reads from genomic DNA, from either Illumina or PacBio technologies. It expects a certain folder structure in order for it to work. In return, he will perform the following steps : Quality Check (Illumina only), Assembly, Assembly QC, Annotation, BCG Discovery. Quasan will produce his output in a structured way, keeping only essentials files and removing intermediary data. For more information about the expected structure, see chapter about Prerequisites.  


Quasan can be called in 3 differents ways : 
1. Like example 1 and 2, you start from the begining and perform the assembly and all the following steps.
2. Like example 3, 4 and 6, (-ia option, Input Assembly) you only start from the annotation step. This allow you to squeeze in a custom assembly you have made on the side with custom tools and parameters.
3. Like example 5, you only start from the BCG discovery step. This allow you to pass on a custom .gbk file you might have produced with a tool of your choice. 
 

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

[![](https://mermaid.ink/img/pako:eNqNU21PwjAQ_iuXftIoJOo3TEwYICZqImgCuhFybIU1bO3SdpiF8t_t1qHMF-I-tc9brne3LQlFREmHrCRmMbz0rwMO9nvzL-DRe5lOZ9Bq3YCR-B6hRshQKsZXBrr-mGKkZk7-6l86ObQYOkvPMbUOIhZqJjhHWVS8YUmSp4wjoFI0XSQFqFhsLGrAO6my5jXQXqLSeFrnuXpuLTTqGRgfoCbDcMHEV-AyKaiBYZ1W3n5GmbhYSBY1TXAGGUsEN3B3YJ5XWCPCc0_dPqCmSn-G7Bw7PMreHWV77p1PUqzXtkecC41lAw30fVfShtpRCD7PKkl7tVjPmtZh96lhHHwzloIDW7-yTfb1DL37upTBX8TUv9pPHZWb-sQxk-oy8rtcM5WiipulebkKhR2ev7QLkMwlzYTU7VinSVM3ym2v_6F7zBPNqnX4RUnOSUpliiyya74tfQHRMU1pQDr2GKFcByTgO6vLM7vkdBAxLSTpaJnTc4K5Fs8FD_d3p-kztH9M6sDdB2qhD-A)](https://mermaid.live/edit#pako:eNqNU21PwjAQ_iuXftIoJOo3TEwYICZqImgCuhFybIU1bO3SdpiF8t_t1qHMF-I-tc9brne3LQlFREmHrCRmMbz0rwMO9nvzL-DRe5lOZ9Bq3YCR-B6hRshQKsZXBrr-mGKkZk7-6l86ObQYOkvPMbUOIhZqJjhHWVS8YUmSp4wjoFI0XSQFqFhsLGrAO6my5jXQXqLSeFrnuXpuLTTqGRgfoCbDcMHEV-AyKaiBYZ1W3n5GmbhYSBY1TXAGGUsEN3B3YJ5XWCPCc0_dPqCmSn-G7Bw7PMreHWV77p1PUqzXtkecC41lAw30fVfShtpRCD7PKkl7tVjPmtZh96lhHHwzloIDW7-yTfb1DL37upTBX8TUv9pPHZWb-sQxk-oy8rtcM5WiipulebkKhR2ev7QLkMwlzYTU7VinSVM3ym2v_6F7zBPNqnX4RUnOSUpliiyya74tfQHRMU1pQDr2GKFcByTgO6vLM7vkdBAxLSTpaJnTc4K5Fs8FD_d3p-kztH9M6sDdB2qhD-A)


## Prerequisites

Quasan can only work when given a -s STRAIN that can be found on Ilis in the folder /vol/local/1-MBT-collection . You can change this default directory using the -d option. There are several way to start Quasan. The most classic one is to start from the begining. But depending on your need you can also start in the middle of the analysis with custom files.  

- In most cases, you will start the pipeline from the begining. You need only inside the directory STRAIN the **rawdata** directory. You must then create subfolders for the sequencing technology that was used to produce the data. For now, supported are only PacBio and Illumina. Not sure to understand what I am saying ? Just mimic the folder structure of MBT42 on the left of the picture.  

<a href="https://ibb.co/Y03KGxk"><img src="https://i.ibb.co/mNGY73q/Screenshot-2022-01-26-at-10-49-59.png" alt="Screenshot-2022-01-26-at-10-49-59" border="0"></a><br /><a target='_blank' href='https://nl.imgbb.com/'></a><br />

- If you want to run with the -ia option and start only from annotation, and therefore use Quasan with a custom assembly you have made, then you only need the **assembly** directory. *:warning: However, to keep things clean and tidy, I recommend you still build the rawdata directory and populate it with your rawdata.* Place your custom assembly in the fasta format in the **assembly** directory and Quasan will be able to use it for annotation and BCG discovery. If you don't have a custom assembly, then Quasan will just use the most recent fasta file in the assembly folder.  

- If you want to run with the -as option and start from the BCG discovery, and therefore use Quasan with a custom annotation you have made, then you only need the **assembly** directory. *:warning: However, to keep things clean and tidy, I recommend you still build the rawdata directory and the assembly directory and populate them with correct files.* Place your custom annotation in at least .gbk format in any subfolder (can be named prokka, pgap or custom for example). If you don't have a custom annotation and just want to restart the antismash process, then Quasan will just use the most recently created .gbk in the **annotation** subfolders.  

<u> :warning: I insist many times on **the most recent** file. This means recent in the eye of creation date. If you want to use a custom assembly that was made after an other assembly, then you should use the command touch to update the file's date and make it recognizable for Quasan. </u>

After it ran, Quasan will create the folder structure on the right of the picture. Nice and tidy ! Everything is at its right place, in a codified way that is the same for all strains :sparkles: . You will find one folder per type of files, and all intermediary files generated during the analysis were removed to keep only essentials files.  


## Pipeline details

### Versioning of analysis

As you can start and restart Quasan in different ways, every file is created using today's date and the method in which it was created. Here are examples on how each fille will be named for the strain MBT42, created in the 15/02/2022 : 
1. For PacBio assembly : V15.02.22_pacbio_flye.fasta
2. For Illumina assembly : V15.02.22_illumina_shovill_ELS4_shovill.fa *(sorry I forgot I have added _shovill twice ! Too late now)*
3. For hybrid assembly (PacBio + Illumina polishing ) : V15.02.22_flye_polished.fasta
4. Annotation files use the same prefix as the assembly file, and then add "_prokka" or "_pgap" before the extension

### Quasan.log

For each run, Quasan will write everything he has seen and done into its log Quasan.log. The log is created at the root of the STRAIN folder. Here is an example of Quasan's log :

```bash
#Quasan's log on PG2
2022-02-16 11:09:12 - INFO - -------------------------------------------------
2022-02-16 11:09:12 - INFO - ________
2022-02-16 11:09:12 - INFO - \_____  \  __ _______    ___________    ____  
2022-02-16 11:09:12 - INFO -  /  / \  \|  |  \__  \  /  ___/\__  \  /    \ 
2022-02-16 11:09:12 - INFO - /   \_/.  \  |  // __ \_\___ \  / __ \|   |  \ 
2022-02-16 11:09:12 - INFO - \_____\ \_/____/(____  /____  >(____  /___|  / 
2022-02-16 11:09:12 - INFO -        \__>          \/     \/      \/     \/ 
2022-02-16 11:09:12 - INFO - ---------------------- PG2 ----------------------
2022-02-16 11:09:12 - INFO - Started with arguments :
2022-02-16 11:09:12 - INFO - Namespace(antismash=False, bioproject='PRJNA9999999', biosample='SAMN99999999', buscoLineage='actinobacteria_phylum_odb10', debug=False, estimatedGenomeSize='7.5m', genus='Streptomyces', gram='pos', indir='/vol/local/1-MBT-collection', input_assembly=False, locustag='TMLOC', memory=16, pgap=False, ressources='/vol/local/ressources', strain='PG2', threads='10') 
2022-02-16 11:09:12 - INFO - ---------- Creating folder /vol/local/1-MBT-collection/PG2/multiqc .
2022-02-16 11:09:12 - INFO - ----- PARSING READS
2022-02-16 11:09:12 - INFO - ---------- Detected a folder for pacbio technology
2022-02-16 11:09:12 - INFO - ---------- Added fastq file PG2.fastq.gz from directory /vol/local/1-MBT-collection/PG2/rawdata/pacbio 
2022-02-16 11:09:12 - INFO - ---------- Found a bam file PG2.bam , probably from PacBio. Checking if fastq already exist.
2022-02-16 11:09:12 - INFO - ---------- Corresponding fastq /vol/local/1-MBT-collection/PG2/rawdata/pacbio/PG2.fastq.gz already existing, skipping conversion.
2022-02-16 11:09:12 - INFO - --- Starting the pipeline ! 
2022-02-16 11:09:12 - INFO - --- First part : Reads QC -> Assembly
2022-02-16 11:09:12 - INFO - ----- QC STARTS
2022-02-16 11:09:12 - INFO - ----- ASSEMBLY STARTS
2022-02-16 11:09:12 - INFO - ---------- Creating folder /vol/local/1-MBT-collection/PG2/assembly.
2022-02-16 11:09:12 - INFO - ---------- Only PacBio reads are available, starting assembly with flye.
2022-02-16 11:09:12 - INFO - ---------- Expected file "/vol/local/1-MBT-collection/PG2/assembly/V16.02.22_pacbio_flye_PG2.fasta" is not present, starting assembly process.
2022-02-16 11:09:12 - INFO - ---------- Creating folder /vol/local/1-MBT-collection/PG2/assembly/flye.
2022-02-16 11:09:12 - INFO - ---------- Starting now Flye with command : flye --pacbio-raw /vol/local/1-MBT-collection/PG2/rawdata/pacbio/PG2.fastq.gz --out-dir /vol/local/1-MBT-collection/PG2/assembly/flye --threads 10 --genome-size 7.5m --asm-coverage 50 
2022-02-16 11:24:23 - INFO - ---------- Cleaning up extra files...
2022-02-16 11:24:23 - INFO - ---------- Produced assembly {flye_assembly}, yaaay !
2022-02-16 11:24:23 - INFO - ----- ASSEMBLY DONE
2022-02-16 11:24:23 - INFO - --- Second part : Annotation -> QC 
2022-02-16 11:24:23 - INFO - ----- ANNOTATION START
2022-02-16 11:24:23 - INFO - ---------- Creating folder /vol/local/1-MBT-collection/PG2/annotation/prokka .
2022-02-16 11:24:23 - INFO - ---------- Starting prokka with command : prokka --centre MBT --genus Streptomyces --species sp. --strain PG2 --outdir /vol/local/1-MBT-collection/PG2/annotation/prokka --prefix V16.02.22_pacbio_flye_PG2_prokka --gcode 11 --cpu 10 --locustag TMLOC --addgenes --gram pos --rfam --force /vol/local/1-MBT-collection/PG2/assembly/V16.02.22_pacbio_flye_PG2.fasta .
2022-02-16 11:31:00 - INFO - ---------- Moving report file to multiqc directory...
2022-02-16 11:31:00 - INFO - ----- GENOMES QC STARTED 
2022-02-16 11:31:00 - INFO - ---------- BUSCO STARTED 
2022-02-16 11:31:25 - INFO - ---------- BUSCO DONE 
2022-02-16 11:31:25 - INFO - ---------- Gathering essential results files
2022-02-16 11:31:25 - INFO - ---------- Removing extra files.
2022-02-16 11:31:25 - INFO - ---------- QUAST STARTED 
2022-02-16 11:31:27 - INFO - ---------- QUAST DONE 
2022-02-16 11:31:27 - INFO - ---------- Gathering essential results files
2022-02-16 11:31:27 - INFO - ---------- Removing extra files.
2022-02-16 11:31:27 - INFO - ----- GENOMES QC DONE 
2022-02-16 11:31:27 - INFO - ----- COMPILING RESULTS WITH MULTIQC
2022-02-16 11:31:29 - INFO - --- Third part : BGC discovery 
2022-02-16 11:31:29 - INFO - ----- ANTISMASH STARTED 
2022-02-16 11:31:29 - INFO - ---------- Starting antismash with command : antismash --genefinding-tool none --cpus 10 --clusterhmmer --tigrfam --smcog-trees --cb-general --cb-subcluster --cb-knownclusters --asf --rre --cc-mibig --output-dir /vol/local/1-MBT-collection/PG2/antismash --html-title PG2 /vol/local/1-MBT-collection/PG2/annotation/prokka/V16.02.22_pacbio_flye_PG2_prokka.gbk .
2022-02-16 11:45:29 - INFO - ----------------------Quasan has ended  (•̀ᴗ•́)و -------------------
```

### Quality Control

- The quality control of raw reads is performed only for Illumina reads, using the tool **FASTQC**.
- Assemblies qualities are assessed using **BUSCO** and **QUAST**
- All results are compiled using **MULTIQC**

### Assembly

- When only PacBio data are present, an assembly is generated using **FLYE**.
- When only Illumina data are present, an assembly is generated using **SHOVILL** (a wrapper of Spades)
- When both Illumina and PacBio data are available, first an assembly using **FLYE** will be made with PacBio reads, then this assembly will be polished with **PILON** using Illumina reads, after the reads were aligned against the PacBio only assembly using BOWTIE2

### Annotation

- By default, the annotation is generated with **PROKKA**
- Using the --pgap option on Ilis, you can also use **PGAP** for easier upload on NCBI :warning: Does not work on genomes with too many contigs
