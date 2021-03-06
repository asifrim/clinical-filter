### Clinical filtering for trios

Find variants in affected children that might contribute to their disorder. We
load VCF files (either named on the command line, or listed in a PED file) for
members of a family, filter for rare, functionally disruptive variants, and
assess whether each variant might affect the child's disorder. We take into
account the parents genotypes (if available) and whether the parents are also
affected with a (the?) disorder. For variants in known disease causative genes
we check whether the inheritance patterns matches one expected for the
inheritance models of the gene.

Standard usage:
```sh
python clinical_filter.py \
  --ped temp_name.ped \
  --syndrome-regions regions_filename.txt \ # optional
  --known-genes known_genes.txt \ # optional (but recommended)
  --known-genes-date 2014-01-01 \ # optional
  --alternate-ids alternate_ids.txt \ # optional
  --output output_name.txt \ # optional
  -export-vcf vcf_filename_or_directory # optional
```

For running the filtering, the basic command is either with a ped file
specified, i.e.

```sh
python clinical_filter.py \
  --ped PED_PATH
```

Or the individual VCF files for a trio can be specified, i.e.

```sh
python clinical_filter.py \
  --child CHILD_VCF_PATH \
  --mother MOTHER_VCF_PATH \
  --father FATHER_VCF_PATH \
  --mom-aff MOM_AFFECTED_STATUS (1=unaffected or 2=affected) \
  --dad-aff DAD_AFFECTED_STATUS (1=unaffected or 2=affected)
```

The ped option is the easiest if you have a large number of trios to
process, so you can define all the families and their VCF paths in the ped
file, and run with that.

Other options are:
 * `--syndrome-regions SYNDROMES_PATH` # path to file listing DECIPHER regions
 * `--known-genes KNOWN_GENES_PATH` # to specify the DDG2P database file
 * `--known-genes-date 2014-01-01` # to specify the version of the known genes file
 * `--alternate-ids ALTERNATE_IDS_PATH` # path to file for mapping individuals
   between IDs used in the PED file, to alternate study IDs.
 * `--output OUTPUT_PATH` # to specify that you want tab-separated output
   written to the given path
 * `--export-vcf OUTPUT_VCF_PATH` # to specify you want a filtered VCF, can
   give a directory (when analysing multiple individuals), or give a file path

The output options can be omitted, or used together, whichever you need.
