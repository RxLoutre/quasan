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
    parser.add_argument("-a", "--assembly",
                        help=argparse.SUPPRESS, required=False, action='store_true')
    parser.add_argument("-an", "--annotation",
                        help=argparse.SUPPRESS, required=False, action='store_true')
    parser.add_argument("-q", "--qualitycheck",
                        help=argparse.SUPPRESS, required=False, action='store_true')
    parser.add_argument("-as", "--antismash",
                        help=argparse.SUPPRESS, required=False, action='store_true')
    parser.add_argument("-bs", "--bigscape",
                        help=argparse.SUPPRESS, required=False, action='store_true')
    parser.add_argument("--all", "--all",
                        help=argparse.SUPPRESS, required=False, action='store_true')
    parser.add_argument("--logfile", "--logfile",
                        help=argparse.SUPPRESS, required=False, default="Quasan.log")
    return (parser.parse_args())
 
def parse_reads(logger,workdir):
	files = os.listdir(workdir)
	reads = []
	for read_file in files:
		name, extension = os.path.splitext(read_file)
		if(extension == '.gz'):
			name, extension = os.path.splitext(name)
		if(extension == '.fastq' or extension == '.fq'):
			logger.info('Found fastq file : {}'.format(read_file))
			read_path = workdir + '/' + read_file
			reads.append(read_path)
		else:
			logger.info('The file {} is not a fastq file.. But a {} file (⊙_☉)'.format(name,extension))
	return reads
	
def assembly_illumina(logger,reads,workdir,tag):
	R1 = reads[0]
	R2 = reads[1]
	try:
		cmd_assembly = f"shovill --outdir {workdir}/shovill --R1 {R1} --R2 {R2}"
		res_assembly = subprocess.check_output(cmd_assembly, shell=True)
		final_assembly = workdir + "/shovill/contigs.fa"
		final_assembly_graph = workdir + "/shovill/contigs.gfa"
		shovill_assembly = workdir + "/" + tag + "_shovill.fa"
		shovill_assembly_graph = workdir + "/" + tag + "_shovill.gfa"
		logger.info('Saving only usefull files.')
		os.replace(final_assembly,shovill_assembly)
		os.replace(final_assembly_graph,shovill_assembly_graph)
		shutil.rmtree(workdir+"/shovill")
	except Exception as e:
		logger.info('---------- Shovill ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
		
def qc_illumina(logger,reads,workdir):
	R1 = reads[0]
	R2 = reads[1]
	try:
		cmd_fastqc = f"fastqc {R1} {R2} -o {workdir} -t 16"
		subprocess.check_output(cmd_fastqc, shell=True)
	except Exception as e:
		logger.info('---------- FastQC ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
		
def qc_assembly(logger,assembly,workdir,tag):
	wdir_busco = workdir + "/busco"
	wdir_quast = workdir + "/quast"
	try:
		busco_lineage = "streptomycetales_odb10"
		cmd_busco = f"busco -i {assembly} -o {tag} --out_path {wdir_busco} -l {busco_lineage} -m geno -f"
		subprocess.check_output(cmd_busco, shell=True)
	except Exception as e:
		logger.info('---------- Busco ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise
	try:
		cmd_quast = f"quast -o {wdir_quast} {assembly}"
		subprocess.check_output(cmd_quast, shell=True)
	except Exception as e:
		logger.info('---------- Quast ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def multiqc(logger,workdir):
	try:
		cmd_multiqc = f"multiqc {workdir} -o {workdir}/multiqc"
		subprocess.check_output(cmd_multiqc, shell=True)
	except Exception as e:
		logger.info('---------- MultiQC ended unexpectedly :( ')
		logger.error(e, exc_info=True)
		raise

def main():
	args = get_arguments()
	#If args.indir = /my/path/STRAIN_XX, then tag = STRAIN_XX
	tag = os.path.basename(args.indir)
	#/!\ DEV : If several sequencing technology, adapt assembly step
	reads_folder = args.indir + "/raw-reads"
	illumina_reads_folder = reads_folder + "/illumina"
	#-----------------------Init logging--------------------------
	try:
		logger = logging.getLogger('quasan_logger')
		logger.setLevel(logging.DEBUG)
		fh = logging.FileHandler(args.logfile)
		fh.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	except:
		print("No permissions to write the logs at {args.logfile}. Fine, no logs then :/")
		raise # indicates that user has no write permission in this directory. No logs then
	
	logger.info('-------------------QUASAN - {}-----------------------'.format(tag))
	logger.info('Started with arguments :')
	logger.info('{} '.format(args))
	#------------------------Reads parsing----------------------
	reads = parse_reads(logger,illumina_reads_folder)

	#-----------------------Quality check-----------------------
	if args.qualitycheck:
		logger.info('Starting QC procedure for {tag}')
		reads_qc_dir = reads_folder + '/QC'
		if not (os.path.isdir(reads_qc_dir)):
			os.mkdir(reads_qc_dir)
		qc_illumina(reads,reads_qc_dir)
		logger.info('QC is over !')
		
	#-----------------------Assembly----------------------------
	if args.assembly:
		logger.info('----- ASSEMBLY START')
		assembly_dir = args.indir + '/assembly'
		assembly_file = assembly_dir + "/" + tag + "_shovill.fa"
		if not (os.path.isdir(assembly_dir)):
			logger.info('---------- Creating folder {}.'.format(assembly_dir))
			os.mkdir(assembly_dir)
		else:
			logger.info('---------- Folder already existing, checking if assembly is nearby.')
			if (os.path.isfile(assembly_file)):
				logger.info('---------- The assembly {} already exist, skipping directly to QC.'.format(assembly_file))
				qc_assembly(logger,assembly_file,assembly_dir,tag)
			else:
				logger.info('---------- Expected file "{}" is not present, starting assembly process.'.format(assembly_file))
				assembly_illumina(reads,assembly_dir,tag)
				qc_assembly(assembly_file,assembly_dir,tag)
		logger.info('----- ASSEMBLY DONE')
			
	logger.info('Quasan has ended  (•̀ᴗ•́)و')

if __name__ == '__main__':
    main()
