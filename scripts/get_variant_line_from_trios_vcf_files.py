
from __future__ import print_function

import gzip
import os
import argparse

USER_FOLDER = "/nfs/users/nfs_j/jm33/"
PED_FILE = os.path.join(USER_FOLDER, "exome_reporting.ped")

def get_options():
    """ gets the options from the command line
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--individual', dest='proband_ID', \
        required=True, help='ID of proband to be analysed')
    parser.add_argument('--chrom', help='chrom of variant')
    parser.add_argument('--position', help='position')
    parser.add_argument('--ped', help='path to ped file')
    
    args = parser.parse_args()
    
    return args

def load_ped(ped_path, proband_ID):
    """ loads the pedigree details for a prband
    """
    
    ped = open(ped_path, "r")
    ped_read = ped.readlines()
    ped.close()
    
    # find the maternal and paternal IDs for the individual
    for line in ped_read:
        line = line.split()
        individual_ID = line[1]
        
        if individual_ID == proband_ID:
            family_ID = line[0]
            paternal_ID = line[2]
            maternal_ID = line[3]
            break
    
    # extract all the lines for the individual
    new_ped_lines = []
    for line in ped_read:
        split_line = line.strip().split()
        individual_ID = split_line[1]
        
        if individual_ID == proband_ID or individual_ID == paternal_ID or individual_ID == maternal_ID:
            new_ped_lines.append(line)
    
    return new_ped_lines

def load_single_position(vcf_path, chrom_name, position):
    """ loads records from a VCF file for a single chromosome
    
    Args:
        vcf_path: path to vcf file
        chrom_name: chromosome to select
    
    Returns:
        returns a list of VCF lines that are for a single chromosome
    """
    
    # open the VCF file
    f =  gzip.open(vcf_path,'r')
    
    # remove the header
    for line in f:
        if not line.startswith("#"):
            break
        if line.startswith("##fileformat"):
            continue
    
    # select the lines for a single chromosome, at a single position
    for line in f:
        if line[:7].split("\t")[0] == chrom_name and line[:30].split("\t")[1] == position:
            return line
    
    return []

def parse_vcf_lines(vcf_records):
    """ organises the information in VCF lines into a dictionary format, indexed by chr position.
    
    Args:
        vcf_records: a list of VCF lines for a single individual.
    
    Returns:
        a dictionary of VCF records, indexed by nucleotide position
    """
    
    variants = {}
    for record in vcf_records:
        line = record.strip().split("\t")
        
        pos = line[1]
        variants[pos] = {}
        variants[pos]["position"] = pos
        variants[pos]["chrom"] = line[0]
        variants[pos]["ID"] = line[2]
        variants[pos]["ref_allele"] = line[3]
        variants[pos]["alt_allele"] = line[4]
        variants[pos]["qual"] = line[5]
        variants[pos]["filter"] = line[6]
        
        # split the info line into key value pairs that can be placed in the dictionary
        info = line[7]
        for item in info.split(";"):
            if "=" in item:
                key, value = item.split("=")
            else:
                key, value = item, "1"
            variants[pos][key] = value
        
        # split the format and genotype fields into key value pairs
        tag_labels = line[8].split(":") # the first item in formats are the tags DP:FP:ETC
        tag_values = line[9].split(":") # the second item are the corresponding values.
        variants[pos].update(dict(zip(tag_labels, tag_values)))
        
    return variants

def find_single_position(proband_ID, vcf_path, chromosome, position):
    """finds variants on single chromosome at a single position
    
    Args:
        proband_ID: individual ID string
        vcf_path: path to vcf file for the individual
        output: output file object to write data to
    
    Returns:
        parsed vcf record for the variant
    """
    
    vcf_records = load_single_position(vcf_path, chromosome, position)
    vcf = parse_vcf_lines(vcf_records)
    
    return vcf
        

def main():
    """
    """
    
    options = get_options()
    proband_ID = options.proband_ID
    chromosome = options.chrom
    position = options.position
    
    ped_path = options.ped
    if options.ped is None:
        ped_path = PED_FILE
    
    new_ped = load_ped(ped_path, proband_ID)
    
    for line in new_ped:
        line = line.split()
        individual_ID = line[1]
        
        if individual_ID == proband_ID:
            family_ID = line[0]
            paternal_ID = line[2]
            maternal_ID = line[3]
            proband_vcf_path = line[6]
    
    for line in new_ped:
        line = line.split()
        individual_ID = line[1]
        
        if individual_ID == paternal_ID:
            paternal_vcf_path = line[6]
        if individual_ID == maternal_ID:
            maternal_vcf_path = line[6]
            maternal_vcf_path = line[6]
    
    proband_vcf = find_single_position(proband_ID, proband_vcf_path, chromosome, position)
    maternal_vcf = find_single_position(proband_ID, maternal_vcf_path, chromosome, position)
    paternal_vcf = find_single_position(proband_ID, paternal_vcf_path, chromosome, position)
    
    print(proband_vcf)
    print(maternal_vcf)
    print(paternal_vcf)


if __name__ == '__main__':
    main()

