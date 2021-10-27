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


def get_arguments():
	"""Parsing the arguments"""
	parser = argparse.ArgumentParser(description="",
                                     usage='''
______________________________________________________________________
  Quasan: (*Qu*ality - *As*sembly - *An*alysis )
  A pipeline for assessing quality of raw Illumina reads, performing
  assembly steps and starting secondary analysis (such as anti-smash and
  big-scape).
  Requires to be ran into a proper conda environment containing all
  the dependencies.
______________________________________________________________________
Generic command: python3.py [Options]* -D [input dir]

Create an output directory inside the input directory for each steps.
Will behave differently depending on the given options.

Mandatory arguments:
    -D   Specify the path to the directory for a given strain. The
         directory is expected to have a least this minimal structure :
         MY_SPECIEs
         └──rawdata
            ├── illumina
            ├── (pacbio)
            └── (nanopore)
         With reads in at least the Illumina folder. The pacbio and
         nanopore folder are not mandatory. The directory name will be
         used to name created files.
Options:
    -a  Create a directory named "assembly" inside the input directory
        and perform the assembly with the Shovill pipeline, followed
        by Quast and BUSCO (bacteria) to assess the homemade assembly.
    -an Create a directory named "annotation" inside the input directory
        and perform an annotation step using Prokka. Output will produce
        a GFF3 file that can be used for BCG discovery with AS.
        /!\ Works only if an "assembly" directory exists and contain a
        fasta file.
    -q  Create a directory named "rawdata-QC" and perform a quality check
	    of the reads using FastQC
    -as Create a directory named "antismash" inside the input directory
        and start the BCG discovery using antismash.
        /!\ Works only if an "annotation" directory exists and contain a
        GBK file.
    -bs Create a directory named "big-scape" inside the input directory
        and start the big-scape tool.
        /!\ Works only if an "antismash" directory exists.
    --all Will perform the pipeline entirely. (equivalent to -a -an -q 
    -as -bs)

______________________________________________________________________
''')
	parser.add_argument("-D", "--indir", help=argparse.SUPPRESS, required=True)
	parser.add_argument("-a", "--assembly", help=argparse.SUPPRESS, required=False, action='store_true')
	parser.add_argument("-an", "--annotation", help=argparse.SUPPRESS, required=False, action='store_true')
	parser.add_argument("-q", "--qualitycheck", help=argparse.SUPPRESS, required=False, action='store_true')
	parser.add_argument("-as", "--antismash", help=argparse.SUPPRESS, required=False, action='store_true')
	parser.add_argument("-bs", "--bigscape", help=argparse.SUPPRESS, required=False, action='store_true')
	parser.add_argument("-t", "--threads", help=argparse.SUPPRESS,required=False, default=8)
	parser.add_argument("--all", "--all", help=argparse.SUPPRESS, required=False, action='store_true')
	parser.add_argument("--logfile", "--logfile", help=argparse.SUPPRESS, required=False, default="Quasan.log")
	parser.add_argument("--debug", "--debug", help=argparse.SUPPRESS, required=False, action='store_true')
	return (parser.parse_args())
 
def return_reads(workdir):
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
	reads_dir = os.listdir(workdir)
	reads = {}
	for technology in reads_dir:
		if os.path.isdir(workdir + "/" + technology) and (technology in sequencing_technologies):
			logger.info("---------- Detected a folder for {} technology".format(technology))
			reads[technology] = return_reads(workdir + "/" + technology)
		else:
			logger.debug("---------- Technology {} detected but not supported yet.".format(technology))
	return reads

#/!\ Make a common part for both assemblies ?
def assembly_illumina(reads,workdir,tag):
	R1 = reads[0]
	R2 = reads[1]
	try:
		cmd_assembly = f"shovill --cpus {threads} --outdir {workdir}/shovill --R1 {R1} --R2 {R2} --force"
		#Name of the final output we want to keep in their original folder
		final_assembly = workdir + "/shovill/contigs.fa"
		final_assembly_graph = workdir + "/shovill/contigs.gfa"
		#Renamed file for the final destination with only essentials files
		shovill_assembly = workdir + "/" + tag + "_shovill.fa"
		shovill_assembly_graph = workdir + "/" + tag + "_shovill.gfa"
		
		subprocess.check_output(cmd_assembly, shell=True)
		logger.info('---------- Removing extra files and keeping only fasta files.')
		os.replace(final_assembly,shovill_assembly)
		os.replace(final_assembly_graph,shovill_assembly_graph)
		shutil.rmtree(workdir+"/shovill")
		return shovill_assembly
	except Exception as e:
		logger.error('---------- Shovill ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
		
def qc_illumina(reads):
	R1 = reads[0]
	R2 = reads[1]
	try:
		cmd_fastqc = f"fastqc {R1} {R2} -o {multiqc_dir} -t {threads}"
		subprocess.check_output(cmd_fastqc, shell=True)
	except Exception as e:
		logger.error('---------- FastQC ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def assembly_pacbio(reads,workdir,tag):
	try:
		#Deal better if they are several fastq files for PacBio reads ?
		if isinstance(reads, list):
			reads = reads[0]
		flye_dir = workdir + "/flye"
		cmd_flye = f"flye --pacbio-raw {reads} --out-dir {flye_dir} --threads 16"
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
		logger.info('---------- Removing extra files and keeping only fasta files.')
		os.replace(final_assembly,flye_assembly)
		os.replace(final_assembly_graph,flye_assembly_graph)
		shutil.rmtree(workdir+"/flye")
		logger.info('---------- Produced assembly {flye_assembly}, yaaay !')
		return flye_assembly
	except Exception as e:
		logger.error('---------- Flye ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def polishing(workdir,assembly,reads,tag):
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
	cmd_bowtie = f"bowtie2 -x {index} -1 {R1} -2 {R2} -S {sam} -p {threads}"
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
		cmd_pilon = f"pilon --threads {threads} --genome {assembly} --frags {bam_sorted} --output {polished_assembly} --outdir {assembly_path}"
		logger.info('---------- Starting Pilon with command : {}'.format(cmd_pilon))
		subprocess.check_output(cmd_pilon, shell=True)
	except Exception as e:
		logger.error('---------- Pilon ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	final = assembly_path + "/" + polished_assembly + ".fasta"
	return final

def busco(assembly,workdir):
	wdir_busco = workdir + "/busco"
	wdir_general = multiqc_dir
	busco_dl = ressources_path + "/busco"
	name = os.path.basename(assembly)
	tag, extension = os.path.splitext(name)
	logger.info('---------- BUSCO STARTED ')
	try:
		if(os.path.isfile(assembly)):
			cmd_busco = f"busco -c {threads} -i {assembly} -o {tag} --out_path {wdir_busco} -l {busco_lineage} -m geno --download_path {busco_dl} -f"
			subprocess.check_output(cmd_busco, shell=True)
	except Exception as e:
		logger.error('---------- Busco ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	logger.info('---------- BUSCO DONE ')
	logger.info('---------- Gathering essential results files')
	busco_resume_file = wdir_busco + "/" + tag + "/short_summary.specific." + busco_lineage + "." + tag + ".txt"
	
	busco_resume_file_final = wdir_general + "/short_summary.specific." + busco_lineage + "." + tag + ".txt"
	os.replace(busco_resume_file,busco_resume_file_final)
	logger.info('---------- Removing extra files.')
	shutil.rmtree(wdir_busco)

def quast(workdir,fassemblies):
	wdir_quast = workdir + "/quast"
	wdir_general = multiqc_dir
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
	quast_html_final = wdir_general + "/report.html"
	quast_tsv_final = wdir_general + "/report.tsv"
	os.replace(quast_html,quast_html_final)
	os.replace(quast_tsv,quast_tsv_final)
	logger.info('---------- Removing extra files.')
	shutil.rmtree(wdir_quast)

def annotation(assembly,workdir):
	try:
		if not (os.path.isdir(workdir)):
			logger.info('---------- Creating folder {} .'.format(workdir))
			os.mkdir(workdir)
		else:
			logger.info('---------- Folder {} already existing.'.format(workdir))
		name = os.path.basename(assembly)
		tag, extension = os.path.splitext(name)
		prefix = tag + "_prokka"
		cmd_prokka = f"prokka --outdir {workdir} --prefix {prefix} --gcode 11 --cpu {threads} --addgenes --rfam --force {assembly}"
		logger.info('---------- Starting prokka with command : {} .'.format(cmd_prokka))
		subprocess.check_output(cmd_prokka, shell=True)
		logger.info('---------- Moving report file to multiqc directory...')
		report = workdir + "/" + prefix + ".txt"
		logger.debug('---------- Prokkas report : {}'.format(report))
		report_mqc = multiqc_dir + "/" + prefix + ".txt"
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

def multiqc():
	try:
		cmd_multiqc = f"multiqc {multiqc_dir} -o {multiqc_dir} -f"
		subprocess.check_output(cmd_multiqc, shell=True)
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
	#If args.indir = /my/path/STRAIN_XX, then tag = STRAIN_XX
	tag = os.path.basename(args.indir)
	assembly_dir = args.indir + '/assembly'
	annotation_dir = args.indir + '/annotation'
	global ressources_path
	ressources_path = "/home/boyerr/data_pi-vriesendorpb/ressources/busco"
	global busco_lineage
	busco_lineage = "streptomycetales_odb10"
	global multiqc_dir
	multiqc_dir = args.indir + "/multiqc"
	global threads
	threads = args.threads
	global sequencing_technologies
	sequencing_technologies = ['illumina','pacbio','nanopore']
	reads_folder = args.indir + "/rawdata"
	#-----------------------Init logging--------------------------
	try:
		global logger
		logger = logging.getLogger('quasan_logger')
		if (args.debug):
			logger.setLevel(logging.DEBUG)
		else:
			logger.setLevel(logging.INFO)
		fh = logging.FileHandler(args.logfile)
		if (args.debug):
			fh.setLevel(logging.DEBUG)
		else:
			fh.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	except:
		print("No permissions to write the logs at {}. Fine, no logs then :/".format(args.log))
		pass # indicates that user has no write permission in this directory. No logs then
	
	logger.info('--------------------------------------------------')
	logger.info('________')                                      
	logger.info('\_____  \  __ _______    ___________    ____  ')
	logger.info(' /  / \  \|  |  \__  \  /  ___/\__  \  /    \ ')
	logger.info('/   \_/.  \  |  // __ \_\___ \  / __ \|   |  \ ')
	logger.info('\_____\ \_/____/(____  /____  >(____  /___|  / ')
	logger.info('       \__>          \/     \/      \/     \/ ')
	logger.info('---------------------- {} ----------------------'.format(tag))
	logger.info('Started with arguments :')
	logger.info('{} '.format(args))
	if (not os.path.isdir(multiqc_dir)):
		logger.info('---------- Creating folder {} .'.format(multiqc_dir))
		os.mkdir(multiqc_dir)
	#------------------------Reads parsing----------------------
	logger.info('----- PARSING READS')
	reads = parse_reads(reads_folder)

	#-----------------------Quality check-----------------------
	if args.qualitycheck:
		logger.info('----- READS QC START')
		#Add a test here for if Illumina or PacBio. meanwhile when you have pacbio data don't use -q
		qc_illumina(reads["illumina"])
		logger.info('----- READS QC DONE')
		
	#-----------------------Assembly----------------------------
	if args.assembly:
		logger.info('----- ASSEMBLY START')
		if not (os.path.isdir(assembly_dir)):
			logger.info('---------- Creating folder {}.'.format(assembly_dir))
			os.mkdir(assembly_dir)
		ndate = datetime.datetime.now()
		version = ndate.strftime("V%d.%m.%y")
		techno_available = reads.keys()
		assembly_file = ""
		if ("illumina" in techno_available) and ("pacbio" in techno_available):
			logger.info('---------- Both Illumina reads and PacBio reads are available, starting flye assembly + pilon polishing.')
			tag = version + "_" + "hybrid_flye-pilon_" + tag
			assembly_file = assembly_pacbio(reads["pacbio"],assembly_dir,tag)
			assembly_file = polishing(args.indir,assembly_file,reads["illumina"],tag)
		elif ("illumina" in techno_available):
			logger.info('---------- Only Illumina reads are available, starting assembly with shovill .')
			tag = version + "_" + "illumina_shovill_" + tag
			assembly_file = assembly_illumina(reads["illumina"],assembly_dir,tag)
		elif ("pacbio" in techno_available):
			logger.info('---------- Only PacBio reads are available, starting assembly with flye.')
			tag = version + "_" + "pacbio_flye_" + tag
			assembly_file = assembly_pacbio(reads["pacbio"],assembly_dir,tag)
		logger.info('----- ASSEMBLY DONE')
	
	#-----------------------Annotation---------------------------
	if args.annotation:
		logger.info('----- ANNOTATION START')
		assemblies = glob.glob(assembly_dir+'/*.f*a')
		for assembly in assemblies:
			logger.info('---------- Starting annotation for assembly {}'.format(assembly))
			annotation(assembly,annotation_dir)
	#--------------------------MultiQc---------------------------
	logger.info('----- GENOMES QC STARTED ')
	assemblies = glob.glob(assembly_dir+'/*.f*a')
	list_assemblies = ""
	for assembly in assemblies:
		logger.debug('---------- Started for {} '.format(assembly))
		busco(assembly,assembly_dir)
		to_add = assembly + " "
		list_assemblies += to_add
	#If its stupid but it works, then its not stupid
	#list_assemblies = list_assemblies[:-2]
	quast(assembly_dir,list_assemblies)
	logger.info('----- GENOMES QC DONE ')
	logger.info('----- COMPILING RESULTS WITH MULTIQC')
	multiqc()	
	logger.info('----------------------Quasan has ended  (•̀ᴗ•́)و -------------------' )

if __name__ == '__main__':
    main()
