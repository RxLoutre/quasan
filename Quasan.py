#!/usr/bin/env python3

"""
--------------- MGC/BGC module ---------------
Author: Roxane Boyer
University: Leiden University
Department: Bioinformatics
Date: 26/04/2021
----------------------------------------------
"""

# Import statements
import argparse
import subprocess
import logging
import os
import shutil
from typing import Sequence
import glob
import datetime
import re
import sys
import yaml


def get_arguments():
	"""Parsing the arguments"""
	parser = argparse.ArgumentParser(description="",
                                     usage='''
______________________________________________________________________
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
Meant to be run only on Ilis as many path are hard written, but could be adapted
Requires to be ran into a proper conda environment containing all the dependencies.
______________________________________________________________________
Generic command: python3 Quasan.py [Options]* -s [MBTXX]

Mandatory arguments:
    -ds  Specify the strain.
	The directory is expected to have a least this minimal structure :
         MBTXX
         └──rawdata
            ├── illumina
            └── (pacbio)
         With reads in at least the illumina folder. The pacbio folder is not mandatory. 
         MBTXX will be used to name files generated by the pipeline.
        
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
    

______________________________________________________________________
''')
	parser.add_argument("-s", "--strain", help="The strain you wich to work on.", required=True)
	parser.add_argument("-d", "--indir", help="The directory on Ilis where to look for the strain (default : /vol/local/1-MBT-collection) ", required=False, default="/vol/local/1-MBT-collection")
	parser.add_argument("-ia", "--input_assembly", help="Start the pipeline directly at the annotation step.", required=False, action='store_true')
	parser.add_argument("-as", "--antismash", help="Start the pipeline only from the antismash step.", default=False, action='store_true')
	parser.add_argument("-b", "--buscoLineage", help="The busco lineage to calculate genome completeness against (default : actinobacteria_phylum_odb10)", required=False, default="actinobacteria_phylum_odb10")
	parser.add_argument("-r", "--ressources", help="The ressources folder where to download busco information (default : \"/vol/local/ressources\", when ran on ILis)", required=False, default="/vol/local/ressources")	
	parser.add_argument("-t", "--threads", help="The number of thread to use when using external tools (default : 8)",required=False, default=8)
	parser.add_argument("-m", "--memory", help="The maximum memory to use for all the steps (default : 16)", required=False, default=16)
	parser.add_argument("-e", "--estimatedGenomeSize", help="The genome size you expect. Only used fopr reducing Shovil genome size estimation step. (default : 7,5M)", required=False, default="7.5m")
	parser.add_argument("-g", "--gram", help="The gram type of the bacteria (pos/neg). (default : pos)", required=False, default="pos")
	parser.add_argument("--debug", "--debug", help="Debug mode to print more informations in the log.", required=False, action='store_true')
	parser.add_argument("-ge", "--genus", help="The genus of the bacteria. (default : Streptomyces)", required=False, default="Streptomyces")
	parser.add_argument("--bioproject", "--bioproject", help="If annotation must be submitted to the NCBI, use this option to mention the correct bioproject (default : PRJNA9999999).", default="PRJNA9999999")
	parser.add_argument("--biosample", "--biosample", help="If annotation must be submitted to the NCBI, use this option to mention the correct biosample (default : SAMN99999999).", default="SAMN99999999")
	parser.add_argument("--locustag", "--locustag", help="If annotation must be submitted to the NCBI, use this option to mention the correct locus_tag (default : TMLOC).", default="TMLOC")
	parser.add_argument("--pgap", "--pgap", help="If annotation must be submitted to the NCBI, use this option to run annotation step using PGAP instead of prokka.", action='store_true')
	return (parser.parse_args())
 
def return_reads(workdir):
	# This function parse {workdir} and is looking for files that could be raw reads (.gz accepted), eg .fastq or .fq
	# It return a list of the reads he found in this directory matching the name criteria
	# If input reads from PacBio are in bam format, automatically perform the conversion to fastq.gz
	files = os.listdir(workdir)
	reads = []
	for read_file in files:
		name, extension = os.path.splitext(read_file)
		read_path = workdir + '/' + read_file
		if(extension == '.gz'):
			name, extension = os.path.splitext(name)
		if(extension == '.fastq' or extension == '.fq'):
			logger.info('---------- Added fastq file {} from directory {} '.format(read_file,workdir))
			reads.append(read_path)
		#/!\ To be improved in order not to add twice the same fastq if both fastq and bam are present.
		# Even though downstream we use only the first file	
		elif(extension == '.bam'):
			logger.info('---------- Found a bam file {} , probably from PacBio. Checking if fastq already exist.'.format(read_file))
			converted_reads = workdir + "/" + name + ".fastq.gz"
			if (os.path.isfile(converted_reads)):
				logger.info('---------- Corresponding fastq {} already existing, skipping conversion.'.format(converted_reads))
			else:
				logger.info('---------- The fastq {} isn\' there yet, converting bam to fastq...'.format(converted_reads))
				try:
					cmd_bam2fastq = f"bam2fastq -o {workdir}/{name} {read_path}"
					subprocess.check_output(cmd_bam2fastq, shell=True)
				except Exception as e:
					logger.error('---------- Bam2fastq ended unexpectedly :( ')
					logger.error(e, exc_info=True)
					raise
			read_path = converted_reads
			reads.append(read_path)
		else:
			logger.debug('---------- I dont think we need this file : {} Right (⊙_☉) ?'.format(read_file))
	return reads

def parse_reads(workdir):
	# This function is a wrapper of return_reads and is used to store all kind of different raw data we could have
	# It will only pay attention to directories in "rawdata" directory that has a subdirectory with a name of a known technology
	# You can edit the global variable {sequencing_technologies} if more is needed
	# It returns a dictionnary with sequencing technologies as keys and list of reads as values
	reads_dir = os.listdir(workdir)
	reads = {}
	for technology in reads_dir:
		if os.path.isdir(workdir + "/" + technology) and (technology in sequencing_technologies):
			logger.info("---------- Detected a folder for {} technology".format(technology))
			reads[technology] = return_reads(workdir + "/" + technology)
		else:
			logger.debug("---------- Technology {} detected but not supported yet.".format(technology))
	return reads

def find_R_reads(reads,strand):
	# This function determine from a list of reads which sub-list of reads correspond to the given {strand}
	# Strand can be either "1" or "2"
	# Two patterns were commonly present in paired end technology and I created regexp for those I know
	# /!\ This function might malfunction if the reads name do not correspond to this pattern
	# Will return a list of reads that correspond to either of the known patterns and correspond to the given strand
	R_reads = []
	pattern1_R=".*_R?{}_.*\.f(ast)?q(.gz)?".format(strand)
	pattern2_R=".*R?{}\.f(ast)?q(.gz)?".format(strand)
	for read in reads:
		if((re.match(pattern1_R,read)) or (re.match(pattern2_R,read))):
			logger.info("---------- Read {} is a R{} file.".format(read,strand))
			R_reads.append(read)
	return R_reads

def concat_reads_illumina(workdir,reads):
	# This function might be needed when more than one set of paired-end reads are in the same directory
	# In this case, before assembly, a concatenated fie for each strand must be generated
	# This function returns a double of the concatenated R1 file and concatenated R2 file
	R1_reads = []
	R2_reads = []
	concat_R1_filename = workdir + "/concat_R1.fq.gz"
	concat_R2_filename = workdir + "/concat_R2.fq.gz"
	#/!\ Check if something went wrong with find_R_reads
	R1_reads = find_R_reads(reads,1)
	R2_reads = find_R_reads(reads,2)		
	#Concatenate all R1 together and all R2 together, in correct order normally
	try:
		with open(concat_R1_filename,'wb') as wfp1:
			for fn in R1_reads:
				with open(fn, 'rb') as rfp:
					shutil.copyfileobj(rfp, wfp1)
		logger.info("-------- Concatenated all R1 reads into {} ".format(concat_R1_filename))
		with open(concat_R2_filename,'wb') as wfp2:
			for fn in R2_reads:
				with open(fn, 'rb') as rfp:
					shutil.copyfileobj(rfp, wfp2)
		logger.info("-------- Concatenated all R2 reads into {} ".format(concat_R2_filename))
		return concat_R1_filename,concat_R2_filename
	except Exception as e:
		logger.error("-------- Concat_reads failed to concatenate :( ")
		logger.error(e, exc_info=True)
		sys.exit("Concat_reads failed to concatenate :(")
	

def assembly_illumina(reads,workdir,tag,args):
	# Perform assembly with an "illumina only" approach using reads contained in the list {reads}
	# This function write its output in the {workdir} directory
	# It will rename the assembly generated using the prefix {tag} that is determined beforehand using the date and tool used
	# Also clean up all temporary files and only keep fasta and gfa file
	# If reads needed to be concatenated for the assembly, they will also be removed to save space
	reads_files_nb = len(reads)
	if (reads_files_nb > 2):
		R1, R2 = concat_reads_illumina(workdir,reads)
	else:
		R1 = reads[0]
		R2 = reads[1]
	try:
		cmd_assembly = f"shovill --cpus {args.threads} --outdir {workdir}/shovill --R1 {R1} --R2 {R2} --force --gsize {args.estimatedGenomeSize} --ram {args.memory}"
		#Name of the final output we want to keep in their original folder
		final_assembly = workdir + "/shovill/contigs.fa"
		final_assembly_graph = workdir + "/shovill/contigs.gfa"
		#Renamed file for the final destination with only essentials files
		shovill_assembly = workdir + "/" + tag + "_shovill.fa"
		shovill_assembly_graph = workdir + "/" + tag + "_shovill.gfa"		
		subprocess.check_output(cmd_assembly, shell=True)
		logger.info('---------- Cleaning up extra files...')
		os.replace(final_assembly,shovill_assembly)
		os.replace(final_assembly_graph,shovill_assembly_graph)
		#if there is a concat files, remove it !
		if(os.path.isfile(workdir + "/concat_R1.fq.gz")):
			os.remove(workdir + "/concat_R1.fq.gz")
		if(os.path.isfile(workdir + "/concat_R2.fq.gz")):
			os.remove(workdir + "/concat_R2.fq.gz")
		shutil.rmtree(workdir+"/shovill")
		return shovill_assembly
	except Exception as e:
		logger.error('---------- Shovill ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def qc_illumina(reads,outdir,args):
	# This function perform the initial raw reads {reads} QC using fastqc
	# /!\ For now read QC is only performed on illumina data
	# Write its output in {outdir}, whcih should be a location that multiqc is able to parse later
	reads_files_nb = len(reads) // 2
	R1_reads = []
	R2_reads = []
	R1_reads = find_R_reads(reads,"1")
	R2_reads = find_R_reads(reads,"2")
	logger.info('----- READS QC START')
	try:
		for i in range(0,reads_files_nb):
			R1 = R1_reads[i]
			R2 = R2_reads[i]
			cmd_fastqc = f"fastqc {R1} {R2} -o {outdir} -t {args.threads}"
			logger.info('-------- Starting command : {}'.format(cmd_fastqc))
			logger.debug('-------- i = {}'.format(i))
			subprocess.check_output(cmd_fastqc, shell=True)
		logger.info('----- READS QC ENDED')
	except Exception as e:
		logger.error('---------- FastQC ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def assembly_pacbio(reads,workdir,tag,args):
	# Perform assembly with an "pacbio only" approach using reads contained in the list {reads}
	# This function write its output in the {workdir} directory
	# It will rename the assembly generated using the prefix {tag} that is determined beforehand using the date and tool used
	# Also clean up all temporary files and only keep fasta and gfa file
	try:
		# /!\ Deal better if they are several fastq files for PacBio reads ?
		if isinstance(reads, list):
			reads = reads[0]
		flye_dir = workdir + "/flye"
		cmd_flye = f"flye --pacbio-raw {reads} --out-dir {flye_dir} --threads {args.threads} --genome-size {args.estimatedGenomeSize} --asm-coverage 50"
		#Name of the final output we want to keep in their original folder
		final_assembly = flye_dir + "/assembly.fasta"
		final_assembly_graph = flye_dir + "/assembly_graph.gfa"
		#Renamed file for the final destination with only essentials files
		flye_assembly = workdir + "/" + tag + ".fasta"
		flye_assembly_graph = workdir + "/" + tag + ".gfa"
		if (os.path.isfile(flye_assembly)):
			logger.info('---------- The assembly {} already exist, skipping step.'.format(flye_assembly))
			return flye_assembly
		else:
			logger.info('---------- Expected file "{}" is not present, starting assembly process.'.format(flye_assembly))
			if not (os.path.isdir(flye_dir)):
				logger.info('---------- Creating folder {}.'.format(flye_dir))
				os.mkdir(flye_dir)
		logger.info('---------- Starting now Flye with command : {} '.format(cmd_flye))
		subprocess.check_output(cmd_flye, shell=True)
		logger.info('---------- Cleaning up extra files...')
		os.replace(final_assembly,flye_assembly)
		os.replace(final_assembly_graph,flye_assembly_graph)
		os.replace(flye_dir+"/assembly_info.txt",workdir + "/" + tag + "_assembly_info.txt")
		shutil.rmtree(workdir+"/flye")
		logger.info('---------- Produced assembly {flye_assembly}, yaaay !')
		return flye_assembly
	except Exception as e:
		logger.error('---------- Flye ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def polishing(workdir,assembly,reads,tag,args):
	# Polish the given assembly {assembly} with reads in {reads}
	# This function will perform all necessary steps : alignment, conversion to bam, sorting and polishing
	# I have not tested this module recently
	# /!\ Might need to remove some extra files such as the non sorted bam, the sam etc
	reads_files_nb = len(reads)
	if (reads_files_nb > 2):
		R1, R2 = concat_reads_illumina(workdir,reads)
	else:
		R1 = reads[0]
		R2 = reads[1]
	#Making an index out of the freshly made assembly
	alignement_dir = workdir + "/alignement"
	assembly_path = workdir + "/assembly"
	polished_assembly = tag + "_flye_polished"
	alignement_prefix = "illuminaReadsVS" + tag
	sam = alignement_dir + "/" + alignement_prefix + ".sam"
	bam = alignement_dir + "/" + alignement_prefix + ".bam"
	bam_sorted = alignement_dir + "/" + alignement_prefix + "-sorted.bam"
	index = alignement_dir + "/" + tag
	if not (os.path.isdir(alignement_dir)):
			logger.info('---------- Creating folder {}.'.format(alignement_dir))
			os.mkdir(alignement_dir)
	else:
		logger.info('---------- Folder {} already existing.'.format(alignement_dir))
	try:
		cmd_index = f"bowtie2-build {assembly} {index}"
		logger.info('---------- Starting bowtie2 index for {}'.format(tag))
		subprocess.check_output(cmd_index, shell=True)
	except Exception as e:
		logger.error('---------- Bowtie2-build ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	#Alignement with bowtie
	cmd_bowtie = f"bowtie2 -x {index} -1 {R1} -2 {R2} -S {sam} -p {args.threads}"
	logger.info('---------- Starting bowtie2 alignement with command : {}'.format(cmd_bowtie))
	try:
		subprocess.check_output(cmd_bowtie, shell=True)
	except Exception as e:
		logger.error('---------- Bowtie2 ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	logger.info('---------- Processing alignement...')
	try:
		#Converting to bam
		cmd_samtools1 = f"samtools view -S -b {sam} > {bam} "
		subprocess.check_output(cmd_samtools1, shell=True)
		#Sorting bam
		cmd_samtools2 = f"samtools sort {bam} -o {bam_sorted}"
		subprocess.check_output(cmd_samtools2, shell=True)
		#Indexing for viewing more easily in IGV
		cmd_samtools3 = f"samtools index {bam_sorted}"
		subprocess.check_output(cmd_samtools3, shell=True)
	except Exception as e:
		logger.error('---------- Samtools ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	try:
		cmd_pilon = f"pilon --threads {args.threads} --genome {assembly} --frags {bam_sorted} --output {polished_assembly} --outdir {assembly_path}"
		logger.info('---------- Starting Pilon with command : {}'.format(cmd_pilon))
		subprocess.check_output(cmd_pilon, shell=True)
		#if there is a concat files, remove it !
		if(os.path.isfile(workdir + "/concat_R1.fq.gz")):
			os.remove(workdir + "/concat_R1.fq.gz")
		if(os.path.isfile(workdir + "/concat_R2.fq.gz")):
			os.remove(workdir + "/concat_R2.fq.gz")
	except Exception as e:
		logger.error('---------- Pilon ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	final = assembly_path + "/" + polished_assembly + ".fasta"
	return final

def busco(assembly,workdir,outdir,args):
	# Start BUSCO to measure gene content on the assembly {assembly}
	# By default, using the lineage actinobacteria_phylum_odb10, but can be changed using the option --buscoLineage
	# The lineage and the ressources to use are passed using args
	# Write its output in the {outdir} directory, which is meant to be the multiqc dir
	wdir_busco = workdir + "/busco"
	busco_dl = args.ressources
	name = os.path.basename(assembly)
	tag, extension = os.path.splitext(name)
	logger.info('---------- BUSCO STARTED ')
	try:
		if(os.path.isfile(assembly)):
			cmd_busco = f"busco -c {args.threads} -i {assembly} -o {tag} --out_path {wdir_busco} -l {args.buscoLineage} -m geno --download_path {busco_dl} -f"
			subprocess.check_output(cmd_busco, shell=True)
	except Exception as e:
		logger.error('---------- Busco ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	logger.info('---------- BUSCO DONE ')
	logger.info('---------- Gathering essential results files')
	busco_resume_file = wdir_busco + "/" + tag + "/short_summary.specific." + args.buscoLineage + "." + tag + ".txt"
	
	busco_resume_file_final = outdir + "/short_summary.specific." + args.buscoLineage + "." + tag + ".txt"
	os.replace(busco_resume_file,busco_resume_file_final)
	logger.info('---------- Removing extra files.')
	shutil.rmtree(wdir_busco)

def quast(workdir,fassemblies,outdir):
	# Perform basic statistics (N50, number of contigs etc) on the given assembly file list {fassemblies}
	# Write its output in the {outdir} directory, which is meant to be the multiqc dir
	wdir_quast = workdir + "/quast"
	logger.info('---------- QUAST STARTED ')
	try:
		cmd_quast = f"quast -o {wdir_quast} {fassemblies}"
		subprocess.check_output(cmd_quast, shell=True)
	except Exception as e:
		logger.error('---------- Quast ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	logger.info('---------- QUAST DONE ')
	logger.info('---------- Gathering essential results files')
	quast_html = wdir_quast + "/report.html"
	quast_tsv = wdir_quast + "/report.tsv"
	quast_html_final = outdir + "/report.html"
	quast_tsv_final = outdir + "/report.tsv"
	os.replace(quast_html,quast_html_final)
	os.replace(quast_tsv,quast_tsv_final)
	logger.info('---------- Removing extra files.')
	shutil.rmtree(wdir_quast)

def annotation_prokka(assembly,workdir,report_dir,tag,assembly_version,args):
	# Annotate the asseembly {assembly} and produce its results in the folder {workdir}
	# using {tag} as the strain name and {assembly_version} as the output files name.
	# {report_dir} is passed to store some files used by multiqc for the end assessment of the assembly quality
	# Args are given to access various options for the tool as well as the number of threads
	species="sp."
	centre = "MBT"
	try:
		#-----------------Prep steps------------------
		if not (os.path.isdir(workdir)):
			logger.info('---------- Creating folder {} .'.format(workdir))
			os.makedirs(workdir)
		else:
			logger.info('---------- Folder {} already existing.'.format(workdir))
		prefix = assembly_version + "_prokka"
		#---------------Annotation--------------------
		cmd_prokka = f"prokka --centre {centre} --genus {args.genus} --species {species} --strain {tag} --outdir {workdir} --prefix {prefix} --gcode 11 --cpu {args.threads} --locustag {args.locustag} --addgenes --gram {args.gram} --rfam --force {assembly}"
		logger.info('---------- Starting prokka with command : {} .'.format(cmd_prokka))
		subprocess.check_output(cmd_prokka, shell=True)
		#-----------------Cleaning up-----------------
		logger.info('---------- Moving report file to multiqc directory...')
		report = workdir + "/" + prefix + ".txt"
		logger.debug('---------- Prokkas report : {}'.format(report))
		report_mqc = report_dir + "/" + prefix + ".txt"
		#Rename in the file multiqc the word "strain" by the actual {tag} so it's easier to read in the reports
		fin = open(report,"rt")
		fout = open(report_mqc,"wt")
		for line in fin:
			fout.write(line.replace('strain',tag))
		fin.close()
		fout.close()
	except Exception as e:
		logger.error('---------- Prokka ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def annotation_pgap(assembly,workdir,tag,assembly_version,args):
	# Annotate the asseembly {assembly} and produce its results in the folder {workdir}
	# using {tag} as the strain name and {assembly_version} as the output files name.
	# Args are given to access various options for the tool as well as the number of threads
	#Create a name for a temp outdir for PGAP results
	temp_workdir = workdir + "/" + tag
	temp_assembly = workdir + "/" + tag + "_genomics.fasta"
	yml_input_file = workdir + "/input.yml"
	yml_submol_file = workdir + "/submol.yml"
	yml_input = {'fasta': {'class': 'File', 'location': tag + "_genomics.fasta"}, 'submol': {'class': 'File', 'location': yml_submol_file}}
	yml_submol = {'organism': {'genus_species': 'Streptomyces', 'strain': tag}, 'comment': 'Annotated locally by PGAP within pipeline Streptidy V1.0', 'bioproject': args.bioproject, 'biosample': args.biosample, 'locus_tag_prefix': args.locustag}
	try:
		#-----------------Prep steps------------------
		if not (os.path.isdir(workdir)):
			logger.info('---------- Creating folder {} .'.format(workdir))
			os.makedirs(workdir)
		else:
			logger.info('---------- Folder {} already existing.'.format(workdir))
		if (os.path.isdir(temp_workdir)):
			logger.warning('---------- Folder {} already existing.'.format(temp_workdir))
			logger.warning('---------- PGAP will probably don\'t like that, we better remove it')
			os.rmdir(temp_workdir)
		prefix = assembly_version + "_pgap"
		#Create the yaml files needed for pgap
		logger.info('---------- Creating input yaml file : {}'.format(yml_input_file))		
		file = open(yml_input_file, 'w')
		yaml.dump(yml_input,file,default_flow_style=False,sort_keys=False)
		file.close()
		logger.info('---------- Creating submol yaml file : {}'.format(yml_submol_file))		
		file = open(yml_submol_file, 'w')
		yaml.dump(yml_submol,file,default_flow_style=False,sort_keys=False)
		file.close()
		#Copy assembly file for PGAP not to complain
		logger.info('---------- Copying assembly file for his highness PGAP... : {}'.format(assembly))
		shutil.copyfile(assembly,temp_assembly)
		#---------------Annotation--------------------
		cmd_pgap = f"python3 {pgap_dir}/pgap.py -n -o {temp_workdir} {yml_input_file} --no-internet -D singularity -c {args.threads}"
		logger.info('---------- Starting PGAP with command : {} .'.format(cmd_pgap))
		subprocess.check_output(cmd_pgap, shell=True)
		#-----------------Cleaning up-----------------
		logger.info('---------- Cleaning up temporary files !')
		#Removing the yamls files
		list_yaml = glob.glob(workdir+'/*.yml')
		for ze_yaml in list_yaml:
			os.remove(ze_yaml)
		#Renaming files we want to keep and move them in workdir
		os.replace(temp_workdir+"/annot.faa",workdir+"/"+prefix+".faa")
		os.replace(temp_workdir+"/annot.gbk",workdir+"/"+prefix+".gbk")
		os.replace(temp_workdir+"/annot.gff",workdir+"/"+prefix+".gff")
		os.replace(temp_workdir+"/annot.sqn",workdir+"/"+prefix+".sqn")
		shutil.rmtree(temp_workdir)

	except Exception as e:
		logger.error('---------- PGAP ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def antismash(gbk,workdir,tag,args):
	# This function perform Biosynthethic Gene Cluster discovery on a given gbk file {gbk}
	# Use the prefix {tag} to rename the html file
	# Write all its output in the {workdir} directory
	# /!\ Maybe in the future think about compressing or reducing antismash output
	cmd_antismash = f"antismash --genefinding-tool none --cpus {args.threads} --clusterhmmer --tigrfam --smcog-trees --cb-general --cb-subcluster --cb-knownclusters --asf --rre --cc-mibig --output-dir {workdir} --html-title {tag} {gbk}"
	logger.info('---------- Starting antismash with command : {} .'.format(cmd_antismash))
	try:
		subprocess.check_output(cmd_antismash, shell=True)
	except Exception as e:
		logger.error('---------- Antismash ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
def multiqc(outdir):
	# This function just call multiqc in the dir {outdir}
	# All tools that can be parsed by multiqc should have wrote their report there so multiqc can make one big resume out of it
	# /!\ Maybe in the future, rename the multiqc_report.html into something more friendly/attractive such as "click_me" or "general_report"
	try:
		cmd_multiqc = f"multiqc {outdir} -o {outdir} -f"
		subprocess.check_output(cmd_multiqc, shell=True)
		logger.debug('---------- Renaming final report...')
		os.replace(outdir+"/multiqc_report.html",outdir+"/../final_report.html")
	except Exception as e:
		logger.error('---------- MultiQC ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

#----------------------------------------------------------------------------------
#--------------------------------------MAIN----------------------------------------
#----------------------------------------------------------------------------------
def main():
	#----------------------Args and global------------------------
	args = get_arguments()
	tag = args.strain
	workdir = args.indir + '/' + args.strain
	assembly_dir = workdir + '/assembly'
	annotation_dir = workdir + '/annotation'
	antismash_dir = workdir + '/antismash'
	multiqc_dir = workdir + '/multiqc'
	global sequencing_technologies
	sequencing_technologies = ['illumina','pacbio','nanopore']
	global pgap_dir
	pgap_dir = "/vol/local/pgap"
	reads_folder = workdir + "/rawdata"
	#-----------------------Init logging--------------------------
	try:
		global logger
		logger = logging.getLogger('quasan_logger')
		if (args.debug):
			logger.setLevel(logging.DEBUG)
		else:
			logger.setLevel(logging.INFO)
		fh = logging.FileHandler(args.indir+"/Quasan.log")
		if (args.debug):
			fh.setLevel(logging.DEBUG)
		else:
			fh.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	except:
		print("No permissions to write the logs at {}. Fine, no logs then :/".format(args.indir+"/Quasan.log"))
		pass # indicates that user has no write permission in this directory. No logs then
	
	logger.info('-------------------------------------------------')
	logger.info('________')                                      
	logger.info('\_____  \  __ _______    ___________    ____  ')
	logger.info(' /  / \  \|  |  \__  \  /  ___/\__  \  /    \ ')
	logger.info('/   \_/.  \  |  // __ \_\___ \  / __ \|   |  \ ')
	logger.info('\_____\ \_/____/(____  /____  >(____  /___|  / ')
	logger.info('       \__>          \/     \/      \/     \/ ')
	logger.info('---------------------- {} ----------------------'.format(tag))
	logger.info('Started with arguments :')
	logger.info('{} '.format(args))
	#--------------------Checking input folder------------------
	if (not os.path.isdir(workdir)):
		logger.error('---------- Wait a minute ! I dont see any strain {} in the collection folder {}, are you sure you did not made a mistake ? .'.format(tag,workdir))
		sys.exit('---------- Wait a minute ! I dont see any strain {} in the collection folder {}, are you sure you did not made a mistake ? .'.format(tag,workdir))
	if (not os.path.isdir(multiqc_dir)):
		logger.info('---------- Creating folder {} .'.format(multiqc_dir))
		os.mkdir(multiqc_dir)
	#------------------------Reads parsing----------------------
	logger.info('----- PARSING READS')
	reads = parse_reads(reads_folder)
	techno_available = reads.keys()
	#Maybe one day I will find a nice PacBio QC tool but I doubt it, not a prioritu for now
	#-----------------------Check mode--------------------------
	if not args.antismash:
		logger.info('--- Starting the pipeline ! ')
		if not args.input_assembly:
			logger.info('--- First part : Reads QC -> Assembly')
			assembly_file = ""
			assembly_version = ""
			#--------------------------QC-------------------------------
			logger.info('----- QC STARTS')
			if ("illumina" in techno_available):
				qc_illumina(reads["illumina"],multiqc_dir,args)
			#-----------------------Assembly----------------------------
			logger.info('----- ASSEMBLY STARTS')
			if not (os.path.isdir(assembly_dir)):
				logger.info('---------- Creating folder {}.'.format(assembly_dir))
				os.mkdir(assembly_dir)
			ndate = datetime.datetime.now()
			version = ndate.strftime("V%d.%m.%y")
			if ("illumina" in techno_available) and ("pacbio" in techno_available):
				logger.info('---------- Both Illumina reads and PacBio reads are available, starting flye assembly + pilon polishing.')
				assembly_version = version + "_" + "hybrid_flye-pilon_" + tag
				assembly_file = assembly_pacbio(reads["pacbio"],assembly_dir,assembly_version,args)
				assembly_file = polishing(args.indir,assembly_file,reads["illumina"],tag)
			elif ("illumina" in techno_available):
				logger.info('---------- Only Illumina reads are available, starting assembly with shovill .')
				assembly_version = version + "_" + "illumina_shovill_" + tag
				assembly_file = assembly_illumina(reads["illumina"],assembly_dir,assembly_version,args)
			elif ("pacbio" in techno_available):
				logger.info('---------- Only PacBio reads are available, starting assembly with flye.')
				assembly_version = version + "_" + "pacbio_flye_" + tag
				assembly_file = assembly_pacbio(reads["pacbio"],assembly_dir,assembly_version,args)
			logger.info('----- ASSEMBLY DONE')
			latest_assembly = assembly_file
		else:
			#Find the latest assembly and its prefix
			assemblies = glob.glob(assembly_dir+'/*.fna') + glob.glob(assembly_dir+'/*.fa') + glob.glob(assembly_dir+'/*.fasta')
			latest_assembly = max(assemblies, key=os.path.getctime)
			assembly_version = "custom_" + tag

		#-----------------------Annotation---------------------------
		logger.info('--- Second part : Annotation -> QC ')
		logger.info('----- ANNOTATION START')
		
		logger.debug('---------- Using latest assembly for annotation : '.format(latest_assembly))
		if not (args.pgap):
			annotation_prokka(latest_assembly,annotation_dir+"/prokka",multiqc_dir,tag,assembly_version,args)
		else:
			annotation_pgap(latest_assembly,annotation_dir+"/pgap",tag,assembly_version,args)
		#--------------------------MultiQc---------------------------
		logger.info('----- GENOMES QC STARTED ')
		list_assemblies = ""
		for assembly in assemblies:
			logger.debug('---------- Started for {} '.format(assembly))
			busco(assembly,assembly_dir,multiqc_dir,args)
			to_add = assembly + " "
			list_assemblies += to_add
		quast(assembly_dir,list_assemblies,multiqc_dir)
		logger.info('----- GENOMES QC DONE ')
		logger.info('----- COMPILING RESULTS WITH MULTIQC')
		multiqc(multiqc_dir)
	#------------------------Antismash---------------------------
	#Starting here antismash
	list_gbk = glob.glob(annotation_dir+'/pgap/*.gbk')
	latest_gbk = max(list_gbk, key=os.path.getctime)
	logger.info('--- Third part : BGC discovery ')
	logger.info('----- ANTISMASH STARTED ')
	logger.debug('---------- Started for {} '.format(latest_gbk))
	antismash(latest_gbk,antismash_dir,tag,args)
	logger.info('----------------------Quasan has ended  (•̀ᴗ•́)و -------------------' )

if __name__ == '__main__':
    main()