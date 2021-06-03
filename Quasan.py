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

def get_arguments():
	"""Parsing the arguments"""
	parser = argparse.ArgumentParser(description="",
                                     usage='''
______________________________________________________________________
  Quasan: (Quality - Assembly - Analysis - BCG Discovery )
  A pipeline for assessing quality of raw Illumina reads, performing
  assembly steps and starting secondary analysis such as anti-smash and
  big-scape.
  Requires to be ran into a proper conda environment containing all
  the dependencies.
  DEV : conda activate /Users/roxaneboyer/Bioinformatic/anaconda3/envs/assembly
______________________________________________________________________
Generic command: python3.py [Options]* -D [input dir]

Create an output directory inside the input directory for each steps.
Will behave differently depending on the given options.

Mandatory arguments:
    -D   Specify the path to the directory for a given strain. The
         directory is expected to have a least this minimal structure :
         STRAINXX
         └──raw-reads
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
    -q  Create a directory named "quality-check" inside the raw-reads
        directory and perform a quality check of the reads using FastQC
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
			logger.info('---------- Added fastq file : {} to {} directory'.format(read_file,workdir))
			reads.append(read_path)
		#/!\ To be improved in order not to add twice the same fastq if both fastq and bam are present.
		# Even though downstream we use only the first file	
		elif(extension == '.bam'):
			logger.info('---------- Found a bam file : {} , probably from PacBio. Checking if fastq already exist.'.format(read_file))
			converted_reads = workdir + "/" + name + ".fastq.gz"
			if (os.path.isfile(converted_reads)):
				logger.info('---------- Corresponding fastq {} already existing, skipping conversion.'.format(converted_reads))
			else:
				logger.info('---------- The fastq {} isn\' there yet, converting bam to fastq...'.format(converted_reads))
				try:
					cmd_bam2fastq = f"bam2fastq -o {workdir}/{name} {read_path}"
					subprocess.check_output(cmd_bam2fastq, shell=True)
				except Exception as e:
					logger.info('---------- Bam2fastq ended unexpectedly :( ')
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
		cmd_assembly = f"shovill --outdir {workdir}/shovill --R1 {R1} --R2 {R2} --force"
		final_assembly = workdir + "/shovill/contigs.fa"
		final_assembly_graph = workdir + "/shovill/contigs.gfa"
		shovill_assembly = workdir + "/" + tag + "_shovill.fa"
		shovill_assembly_graph = workdir + "/" + tag + "_shovill.gfa"
		if not (os.path.isdir(workdir)):
			logger.info('---------- Creating folder {}.'.format(workdir))
			os.mkdir(workdir)
		else:
			logger.info('---------- Folder {} already existing, checking if assembly is inside.'.format(workdir))
			if (os.path.isfile(shovill_assembly)):
				logger.info('---------- The assembly {} already exist, skipping step.'.format(shovill_assembly))
				return
			else:
				logger.info('---------- Expected file "{}" is not present, starting assembly process.'.format(shovill_assembly))
		subprocess.check_output(cmd_assembly, shell=True)
		logger.info('---------- Removing extra files and keeping only fasta files.')
		os.replace(final_assembly,shovill_assembly)
		os.replace(final_assembly_graph,shovill_assembly_graph)
		shutil.rmtree(workdir+"/shovill")
		return shovill_assembly
	except Exception as e:
		logger.info('---------- Shovill ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
		
def qc_illumina(reads):
	R1 = reads[0]
	R2 = reads[1]
	try:
		cmd_fastqc = f"fastqc {R1} {R2} -o {multiqc_dir} -t 16"
		subprocess.check_output(cmd_fastqc, shell=True)
	except Exception as e:
		logger.info('---------- FastQC ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def assembly_pacbio(reads,workdir,tag):
	try:
		#Deal better if they are several fastq files for PacBio reads ?
		if isinstance(reads, list):
			reads = reads[0]
		flye_dir = workdir + "/flye"
		cmd_flye = f"flye --pacbio-raw {reads} --out-dir {flye_dir} --threads 8"
		final_assembly = flye_dir + "/assembly.fasta"
		final_assembly_graph = flye_dir + "/assembly_graph.gfa"
		flye_assembly = workdir + "/" + tag + "_flye.fasta"
		flye_assembly_graph = workdir + "/" + tag + "_flye.gfa"
		if not (os.path.isdir(flye_dir)):
			logger.info('---------- Creating folder {}.'.format(flye_dir))
			os.mkdir(flye_dir)
		else:
			logger.info('---------- Folder {} already existing, checking if assembly is inside.'.format(flye_dir))
			if (os.path.isfile(flye_assembly)):
				logger.info('---------- The assembly {} already exist, skipping step.'.format(flye_assembly))
				return
			else:
				logger.info('---------- Expected file "{}" is not present, starting assembly process.'.format(flye_assembly))
		logger.info('---------- Starting now Flye with command : {} '.format(cmd_flye))
		subprocess.check_output(cmd_flye, shell=True)
		logger.info('---------- Removing extra files and keeping only fasta files.')
		os.replace(final_assembly,flye_assembly)
		os.replace(final_assembly_graph,flye_assembly_graph)
		shutil.rmtree(workdir+"/shovill")
		return flye_assembly
	except Exception as e:
		logger.info('---------- Flye ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

#def polishing(assembly,reads):
	
		
def qc_assembly(assembly,workdir,tag):
	wdir_busco = workdir + "/busco"
	wdir_quast = workdir + "/quast"
	wdir_general = multiqc_dir
	busco_dl = ressources_path + "/busco"
	logger.info('---------- BUSCO STARTED ')
	try:
		if(os.path.isfile(assembly)):
			cmd_busco = f"busco -i {assembly} -o {tag} --out_path {wdir_busco} -l {busco_lineage} -m geno --download_path {busco_dl} -f"
			subprocess.check_output(cmd_busco, shell=True)
	except Exception as e:
		logger.info('---------- Busco ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	logger.info('---------- BUSCO DONE ')
	logger.info('---------- QUAST STARTED ')
	try:
		cmd_quast = f"quast -o {wdir_quast} {assembly}"
		subprocess.check_output(cmd_quast, shell=True)
	except Exception as e:
		logger.info('---------- Quast ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	logger.info('---------- QUAST DONE ')
	logger.info('---------- Gathering essential results files')
	busco_resume_file = wdir_busco + "/" + tag + "/short_summary.specific." + busco_lineage + "." + tag + ".txt"
	quast_html = wdir_quast + "/report.html"
	quast_tsv = wdir_quast + "/report.tsv"
	busco_resume_file_final = wdir_general + "/short_summary.specific." + busco_lineage + "." + tag + ".txt"
	quast_html_final = wdir_general + "/report.html"
	quast_tsv_final = wdir_general + "/report.tsv"
	os.replace(busco_resume_file,busco_resume_file_final)
	os.replace(quast_html,quast_html_final)
	os.replace(quast_tsv,quast_tsv_final)
	logger.info('---------- Removing extra files.')
	shutil.rmtree(wdir_busco)
	shutil.rmtree(wdir_quast)

def multiqc():
	try:
		cmd_multiqc = f"multiqc {multiqc_dir} -o {multiqc_dir} -f"
		subprocess.check_output(cmd_multiqc, shell=True)
	except Exception as e:
		logger.info('---------- MultiQC ended unexpectedly :( ')
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
	global ressources_path
	ressources_path = "/Users/roxaneboyer/Bioinformatic/ressources"
	global busco_lineage
	busco_lineage = "streptomycetales_odb10"
	global multiqc_dir
	multiqc_dir = args.indir + "/multiqc"
	global sequencing_technologies
	sequencing_technologies = ['illumina','pacbio','nanopore']
	reads_folder = args.indir + "/raw-reads"
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
	
	logger.info('-------------------QUASAN - {}-----------------------'.format(tag))
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
		qc_illumina(reads["illumina"])
		logger.info('----- READS QC DONE')
		
	#-----------------------Assembly----------------------------
	if args.assembly:
		logger.info('----- ASSEMBLY START')
		assembly_dir = args.indir + '/assembly'
		techno_available = reads.keys()
		assembly_file = ""
		if ("illumina" in techno_available) and ("pacbio" in techno_available):
			logger.info('---------- Both Illumina reads and PacBio reads are available, starting hybrid assembly.')
			assembly_file = assembly_pacbio(reads["pacbio"],assembly_dir,tag)
			#assembly_file = polishing(assembly_file,reads["illumina"])
		elif ("illumina" in techno_available):
			logger.info('---------- Only Illumina reads are available, starting Illumina assembly.')
			assembly_file = assembly_illumina(reads["illumina"],assembly_dir,tag)
		elif ("pacbio" in techno_available):
			logger.info('---------- Only Illumina reads are available, starting Illumina assembly.')
			assembly_file = assembly_pacbio(reads["pacbio"],assembly_dir,tag)
		logger.info('----- ASSEMBLY DONE')
		logger.info('----- ASSEMBLY QC STARTED ')
		qc_assembly(assembly_file,assembly_dir,tag)
		logger.info('----- ASSEMBLY QC DONE ')
	logger.info('----- COMPILING RESULTS WITH MULTIQC')
	multiqc()	
	logger.info('----------------------Quasan has ended  (•̀ᴗ•́)و -------------------' )

if __name__ == '__main__':
    main()
