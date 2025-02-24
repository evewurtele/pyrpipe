#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:21:01 2019

@author: usingh
"""

from pyrpipe import pyrpipe_utils as pu
from pyrpipe import pyrpipe_engine as pe
import os

class Assembly:
    """This class represents an abstract parent class for all programs which can perfrom transcripts assembly.
    """
    def __init__(self):
        self.category="Assembler"
    def perform_assembly(bam_file):
        """Function to perform assembly using a bam file as input. Inherited by all children.
        
                
        :param bam_file: path to input BAM
        :type bam_file: string
        
        :return: path to output GTF or output directory depending on the specific assembly program.
        :rtype: string
        """
        pass

class Stringtie(Assembly):
    """This class represents Stringtie program for transcript assembly.
        
        Parameters
        ----------
        
        reference_gtf: string
            Path to the reference gtf file. If a valid gtf file is provided the option -G will be set to the gtf file. This can't
            be overriden later when calling functions of this class.
        kwargs: dict
            Options passed to stringtie. Some of these could be overridden later when calling functions of this class.
            Format to pass the arguments:
        """
    def __init__(self,reference_gtf="",**kwargs):
        
        super().__init__()
        self.program_name="stringtie"
        #check if stringtie exists
        if not pe.check_dependencies([self.program_name]):
            raise Exception("ERROR: "+ self.program_name+" not found.")
        self.valid_args_list=['-G','--version','--conservative','--rf','--fr','-o','-l',
                            '-f','-L','-m','-a','-j','-t','-c','-s','-v','-g','-M',
                            '-p','-A','-B','-b','-e','-x','-u','-h','--merge','-F','-T','-i']
        
        #keep the passed arguments
        self.passed_args_dict=kwargs
        
        #check the reference GTF
        if len(reference_gtf)>0 and pu.check_files_exist(reference_gtf):
            self.reference_gtf=reference_gtf
            self.passed_args_dict['-G']=reference_gtf
        
    def perform_assembly(self,bam_file,out_dir="",out_suffix="_stringtie",overwrite=True,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Function to run stringtie using a bam file.
                
        Parameters
        ----------
        
        bam_file: string
            path to the bam file
        out_suffix: string
            Suffix for the output gtf file
        overwrite: bool
            Overwrite if output file already exists.
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs: dict
            Options to pass to stringtie. This will override the existing options in self.passed_args_dict (only replace existing arguments and not replace all the arguments).
            
        :return: Returns the path to output GTF file
        :rtype: string
        """
        
        #create path to output file
        fname=pu.get_file_basename(bam_file)
        
        if not out_dir:
            out_dir=pu.get_file_directory(bam_file)
            
        out_gtf_file=os.path.join(out_dir,fname+out_suffix+".gtf")
        
        """
        Handle overwrite
        """
        if not overwrite:
            #check if file exists. return if yes
            if os.path.isfile(out_gtf_file):
                print("The file "+out_gtf_file+" already exists. Exiting..")
                return out_gtf_file
        
        #Add output file name and input bam
        new_opts={"-o":out_gtf_file,"--":(bam_file,)}
        merged_opts={**kwargs,**new_opts}
        
        #call stringtie
        status=self.run_stringtie(verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**merged_opts)
        
        if status:
            #check if sam file is present in the location directory of sraOb
            if pu.check_files_exist(out_gtf_file):
                return out_gtf_file
        else:
            return ""
        
    def stringtie_merge(self,*args,out_suffix="_stringtieMerge",overwrite=True,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Function to run stringtie merge.
        
        Parameters
        ----------
        
        args: tuple
            path to gtf files to merge
        out_suffix: string
            Suffix for output gtf file name
        overwrite: bool
            Overwrite if output file already exists.
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs: dict
            Options to pass to stringtie. This will override the existing options in self.passed_args_dict (only replace existing arguments and not replace all the arguments).

        :return: Returns the path to the merged GTF file
        :rtype: string
        """
        
        if len(args) < 1:
            print("ERROR: No input gtf for stringtie merge.")
            return ""
        
        #create path to output sam file
        fname=pu.get_file_basename(args[0])
        out_dir=pu.get_file_directory(args[0])
        out_gtf_file=os.path.join(out_dir,fname+out_suffix+".gtf")
        
        if not overwrite:
            #check if file exists. return if yes
            if os.path.isfile(out_gtf_file):
                print("The file "+out_gtf_file+" already exists. Exiting..")
                return out_gtf_file
        
        #Add merge flag, output file name and input bam
        new_opts={"--merge":"","-o":out_gtf_file,"--":args}
        
        merged_opts={**kwargs,**new_opts}
        
        #call stringtie
        status=self.run_stringtie(verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**merged_opts)
        
        if status:
            #check if sam file is present in the location directory of sraOb
            if pu.check_files_exist(out_gtf_file):
                return out_gtf_file
        else:
            return ""
        
        
        
            
    
    def run_stringtie(self,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running stringtie. This can be used to run stringtie without using perform_assembly() function.
        
        Parameters
        ----------
        
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs: dict
            Options to pass to stringtie. This will override the existing options in self.passed_args_dict (only replace existing arguments and not replace all the arguments).

        :return: Returns the status of stringtie command.
        :rtype: bool
        """
            
        #override existing arguments
        merged_args_dict={**self.passed_args_dict,**kwargs}
       
        stie_cmd=['stringtie']
        #add options
        stie_cmd.extend(pu.parse_unix_args(self.valid_args_list,merged_args_dict))        
        
                
        #start ececution
        status=pe.execute_command(stie_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            pu.print_boldred("stringtie failed")
        
        #return status
        return status
    
    
    
class Cufflinks(Assembly):
    """This class represents cufflinks
    
    kwargs: dict
        Parameters passed to cufflinks
    """
    def __init__(self,reference_gtf="",**kwargs):
        
        super().__init__()
        self.program_name="cufflinks"
        #check if stringtie exists
        if not pe.check_dependencies([self.program_name]):
            raise Exception("ERROR: "+ self.program_name+" not found.")
            
        
        #define valid arguments
        self.cufflinksArgsList=['-h','--help','-o','--output-dir','-p','--num-threads','--seed','-G','--GTF','-g','--GTF-guide','-M','--mask-file','-b','--frag-bias-correct','-u','--multi-read-correct','--library-type','--library-norm-method',
'-m','--frag-len-mean','-s','--frag-len-std-dev','--max-mle-iterations','--compatible-hits-norm','--total-hits-norm','--num-frag-count-draws','--num-frag-assign-draws','--max-frag-multihits','--no-effective-length-correction',
'--no-length-correction','-N','--upper-quartile-norm','--raw-mapped-norm','-L','--label','-F','--min-isoform-fraction','-j','--pre-mrna-fraction','-I','--max-intron-length','-a','--junc-alpha','-A','--small-anchor-fraction',
'--min-frags-per-transfrag','--overhang-tolerance','--max-bundle-length','--max-bundle-frags','--min-intron-length','--trim-3-avgcov-thresh','--trim-3-dropoff-frac','--max-multiread-fraction','--overlap-radius',
'--no-faux-reads','--3-overhang-tolerance','--intron-overhang-tolerance','-v','--verbose','-q','--quiet','--no-update-check']

        self.cuffcompareArgsList=['-h','-i','-r','-R','-Q','-M','-N','-s','-e','-d','-p','-C','-F','-G','-T','-V']
        self.cuffquantArgsList=['-o','--output-dir','-p','--num-threads','-M','--mask-file','-b','--frag-bias-correct','-u','--multi-read-correct','--library-type','-m','--frag-len-mean','-s','--frag-len-std-dev','-c','--min-alignment-count',
'--max-mle-iterations','-v','--verbose','-q','--quiet','--seed','--no-update-check','--max-bundle-frags','--max-frag-multihits','--no-effective-length-correction','--no-length-correction','--read-skip-fraction',
'--no-read-pairs','--trim-read-length','--no-scv-correction']
        self.cuffdiffArgsList=['-o','--output-dir','-L','--labels','--FDR','-M','--mask-file','-C','--contrast-file','-b','--frag-bias-correct','-u','--multi-read-correct','-p','--num-threads','--no-diff','--no-js-tests','-T','--time-series',
'--library-type','--dispersion-method','--library-norm-method','-m','--frag-len-mean','-s','--frag-len-std-dev','-c','--min-alignment-count','--max-mle-iterations','--compatible-hits-norm','--total-hits-norm',
' -v','--verbose','-q','--quiet','--seed','--no-update-check','--emit-count-tables','--max-bundle-frags','--num-frag-count-draws','--num-frag-assign-draws','--max-frag-multihits','--min-outlier-p','--min-reps-for-js-test',
'--no-effective-length-correction','--no-length-correction','-N','--upper-quartile-norm','--geometric-norm','--raw-mapped-norm','--poisson-dispersion','--read-skip-fraction','--no-read-pairs','--trim-read-length','--no-scv-correction']
        self.cuffnormArgsList=['-o','--output-dir','-L','--labels','--norm-standards-file','-p','--num-threads','--library-type','--library-norm-method','--output-format','--compatible-hits-norm','--total-hits-norm','-v','--verbose','-q','--quiet','--seed','--no-update-check']
        self.cuffmergeArgsList=['h','--help','-o','-g','–-ref-gtf','-p','–-num-threads','-s','-–ref-sequence']
        
        self.valid_args_list=pu.get_union(self.cufflinksArgsList,self.cuffcompareArgsList,self.cuffquantArgsList,self.cuffdiffArgsList,self.cuffnormArgsList,self.cuffmergeArgsList)
        
        #keep the passed arguments
        self.passed_args_dict=kwargs
        
        #check the reference GTF
        if len(reference_gtf)>0 and pu.check_files_exist(reference_gtf):
            self.reference_gtf=reference_gtf
            self.passed_args_dict['-g']=reference_gtf
    
    
    def perform_assembly(self,bam_file,out_dir="",out_suffix="_cufflinks",overwrite=True,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Function to run cufflinks with BAM file as input.
                
        Parameters
        ----------
        bam_file: string
            path to bam file
        out_dir: 
            output directory
        out_suffix: string
            Suffix for the output gtf file
        overwrite: bool
            Overwrite if output file already exists.
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession.
        kwargs: dict
            Options to pass to cufflinks. This will override the existing options self.passed_args_dict (only replace existing arguments and not replace all the arguments).

        :return: Returns the path to output GTF file
        :rtype: string       
        """
        
        #create path to output file
        fname=pu.get_file_basename(bam_file)
        if not out_dir:
            out_dir=pu.get_file_directory(bam_file)
        else:
            if not pu.check_paths_exist(out_dir):
                pu.mkdir(out_dir)
        out_gtf_file=os.path.join(out_dir,fname+out_suffix+".gtf")
        
        """
        Handle overwrite
        """
        if not overwrite:
            #check if file exists. return if yes
            if os.path.isfile(out_gtf_file):
                print("The file "+out_gtf_file+" already exists. Exiting..")
                return out_gtf_file
            
        #Add output file name and input bam
        new_opts={"-o":out_dir,"--":(bam_file,)}
        merged_opts={**kwargs,**new_opts}
        
        #call cufflinks
        status=self.run_cufflinks(verbose,quiet,logs,objectid,**merged_opts)
        
        if status:
            #move out_dir/transcripts.gtf to outfile
            pe.move_file(os.path.join(out_dir,"transcripts.gtf"),out_gtf_file)
            #check if sam file is present in the location directory of sraOb
            if pu.check_files_exist(out_gtf_file):
                return out_gtf_file
        else:
            return ""
    
    def run_cuff(self,command,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running cuff* commands
        
        Parameters
        ----------
        
        command: string
            the command name
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession.
        kwargs: dict
            Options passed to command
        
        :return: Returns the status of the command.
        :rtype: bool
        """
        validCommands=['cuffcompare','cuffdiff', 'cufflinks', 'cuffmerge', 'cuffnorm', 'cuffquant']
        if command in validCommands:
            #override existing arguments
            merged_args_dict={**self.passed_args_dict,**kwargs}
       
            cuff_cmd=[command]
            #add options
            cuff_cmd.extend(pu.parse_unix_args(self.valid_args_list,merged_args_dict))        
                  
            #start ececution
            status=pe.execute_command(cuff_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
            if not status:
                pu.print_boldred("cufflinks failed")
                #return status
            return status
        else:
            pu.print_boldred("Unknown command {}"+command)
            return False
    
    
    def run_cufflinks(self,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running cufflinks
        
        Parameters
        ----------
        
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession.
        kwargs: dict
            Options passed to cufflinks
        
        :return: Returns the status of cufflinks command.
        :rtype: bool
        """
            
        #override existing arguments
        merged_args_dict={**self.passed_args_dict,**kwargs}
       
        cufflinks_cmd=['cufflinks']
        #add options
        cufflinks_cmd.extend(pu.parse_unix_args(self.valid_args_list,merged_args_dict))        
        
        
        #start ececution
        status=pe.execute_command(cufflinks_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            pu.print_boldred("cufflinks failed")
        #return status
        return status
    
    
    
class Trinity(Assembly):
    """This class represents Trinity RNA-Seq assembler
    
    kwargs: dict
        parametrs passed to Trinity
    """
    def __init__(self,**kwargs):
        
        super().__init__()
        self.program_name="Trinity"
        self.dep_list=[self.program_name,'jellyfish','bowtie2']
        #check if trinity exists
        if not pe.check_dependencies(self.dep_list):
            raise Exception("ERROR: "+ self.program_name+" not found.")
        
        
        self.valid_args_list=['--seqType','--max_memory','--left','--right','--single','--SS_lib_type','--CPU','--min_contig_length',
                              '--long_reads','--genome_guided_bam','--jaccard_clip','--trimmomatic','--normalize_reads','--no_distributed_trinity_exec',
                              '--output','--full_cleanup','--cite','--verbose','--version','--show_full_usage_info','--KMER_SIZE','--prep','--no_cleanup',
                              '--no_version_check','--min_kmer_cov','--inchworm_cpu','--no_run_inchworm','--max_reads_per_graph','--min_glue','--no_bowtie',
                              '--no_run_chrysalis','--bfly_opts','--PasaFly','--CuffFly','--group_pairs_distance','--path_reinforcement_distance','--no_path_merging',
                              '--min_per_id_same_path','--max_diffs_same_path','--max_internal_gap_same_path','--bflyHeapSpaceMax','--bflyHeapSpaceInit',
                              '--bflyGCThreads','--bflyCPU','--bflyCalculateCPU','--bfly_jar','--quality_trimming_params','--normalize_max_read_cov',
                              '--normalize_by_read_set','--genome_guided_max_intron','--genome_guided_min_coverage','--genome_guided_min_reads_per_partition',
                              '--grid_conf','--grid_node_CPU','--grid_node_max_memory']

        
        #keep the passed arguments
        self.passed_args_dict=kwargs
    
    
    def perform_assembly(self,sra_object=None,bam_file=None,out_dir="trinity_out_dir",max_memory="2G",max_intron=10000,overwrite=True,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Function to run trinity with sra object or BAM file as input.
                
        Parameters
        ----------
        
        sra_object: SRA
            object of SRA class
        bam_file: string
            path to bam file
        out_dir: string
            path to out directory
        max_memory: string
            Max memory argument e.g. "2G"
        max_intron: int
            specify the "--genome_guided_max_intron" argument
        overwrite: bool
            Overwrite if output file already exists
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession.
        
        kwargs: dict
            Options to pass to Trinity. This will override the existing options self.passed_args_dict (only replace existing arguments and not replace all the arguments).

        :return: Return the path to output GTF file
        :rtype: string
        """
        
        #add trinity to outdir
        if "trinity" not in out_dir:
            out_dir+="_trinity"
        
        new_opts={}
        if sra_object is not None:
            parent_dir=sra_object.location
            out_dir=os.path.join(parent_dir,out_dir)
            if sra_object.layout == 'PAIRED':
                new_opts={"--seqType":"fq","--left":sra_object.localfastq1Path,"--right":sra_object.localfastq2Path,"--output":out_dir,"--max_memory":max_memory}
            else:
                new_opts={"--seqType":"fq","--single":sra_object.localfastqPath,"--output":out_dir,"--max_memory":max_memory}
        elif bam_file is not None:
            if not pu.check_files_exist(bam_file):
                pu.print_boldred("Input to trinity does not exist:"+bam_file)
                return ""
            parent_dir=pu.get_file_directory(bam_file)
            out_dir=os.path.join(parent_dir,out_dir)
            new_opts={"--genome_guided_bam":bam_file,"--output":out_dir,"--max_memory":max_memory,"--genome_guided_max_intron":max_intron}
        else:
            pu.print_boldred("Please provide valid input to run trinity")
            return ""
        
        merged_opts={**kwargs,**new_opts}
        
        #call trinity
        status=self.run_trinity(verbose,quiet,logs,objectid,**merged_opts)
        
        if status:
            #check out dir
            if pu.check_paths_exist(out_dir):
                return out_dir
        else:
            return ""

    
    
    def run_trinity(self,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running trinity
        
        Parameters
        ----------
        
        verbose: bool
            Print stdout and std error
        quiet: bool
            Print nothing
        logs: bool
            Log this command to pyrpipe logs
        objectid: str
            Provide an id to attach with this command e.g. the SRR accession.
        kwargs: dict
            Options passed to trinity

        :return: Return the status of trinity command.
        :rtype: bool
        """
            
        #override existing arguments
        merged_args_dict={**self.passed_args_dict,**kwargs}
       
        trinity_cmd=['Trinity']
        #add options
        trinity_cmd.extend(pu.parse_unix_args(self.valid_args_list,merged_args_dict))        
        
        
        #start ececution
        status=pe.execute_command(trinity_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            pu.print_boldred("trinity failed")
        #return status
        return status
    
    
    
    
