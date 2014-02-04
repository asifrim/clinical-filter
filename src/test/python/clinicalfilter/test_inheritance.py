""" unit testing of the Inheritance class
"""

import unittest
from clinicalfilter.ped import Family
from clinicalfilter.ped import Person
from clinicalfilter.variant import Variant
from clinicalfilter.variant_cnv import CNV
from clinicalfilter.variant_snv import SNV
from clinicalfilter.inheritance import Autosomal
from clinicalfilter.vcf_info import VcfInfo
from clinicalfilter.trio_genotypes import TrioGenotypes


class TestInheritancePy(unittest.TestCase):
    """ test the Inheritance class
    """
    
    def setUp(self):
        """ define a family and variant, and start the Inheritance class
        """
        
        # generate a test family
        child_gender = "F"
        mom_aff = "1"
        dad_aff = "1"
        
        self.trio = self.create_family(child_gender, mom_aff, dad_aff)
        
        # generate a test variant
        child_var = self.create_snv(child_gender, "0/1")
        mom_var = self.create_snv("F", "0/0")
        dad_var = self.create_snv("M", "0/0")
        
        var = TrioGenotypes(child_var)
        var.add_mother_variant(mom_var)
        var.add_father_variant(dad_var)
        self.variants = [var]
        
        # make sure we've got known genes data
        self.known_genes = {"TEST": {"inheritance": ["Monoallelic"], "confirmed_status": ["Confirmed DD Gene"]}}
        gene_inh = self.known_genes[var.get_gene()]["inheritance"]
        
        self.inh = Autosomal(self.variants, self.trio, gene_inh)
    
    def create_snv(self, gender, genotype):
        """ create a default variant
        """
        
        chrom = "1"
        pos = "15000000"
        snp_id = "."
        ref = "A"
        alt = "G"
        qual = "50"
        filt = "PASS"
        
        # set up a SNV object, since SNV inherits VcfInfo
        var = SNV(chrom, pos, snp_id, ref, alt, qual, filt)
        
        tags = {"gene": ["HGNC", "VGN", "GN"], "consequence": ["VCQ", "CQ"]}
        
        info = "HGNC=TEST;CQ=missense_variant;random_tag"
        format_keys = "GT:DP"
        sample_values = genotype + ":50"
        
        var.add_info(info, tags)
        var.add_format(format_keys, sample_values)
        var.set_gender(gender)
        var.set_genotype()
        
        return var
    
    def create_family(self, child_gender, mom_aff, dad_aff):
        """ create a default family, with optional gender and parental statuses
        """
        
        fam = Family("test")
        fam.add_child("child", "child_vcf", "2", child_gender)
        fam.add_mother("mother", "mother_vcf", mom_aff, "2")
        fam.add_father("father", "father_vcf", dad_aff, "1")
        fam.set_child()
        
        return fam
    
    def test_check_inheritance_mode_matches_gene_mode(self):
        """ test that check_inheritance_mode_matches_gene_mode() works correctly
        """
        
        # check that the default inheritance types have been set up correctly
        self.assertEqual(self.inh.inheritance_modes, {"Monoallelic", "Biallelic", "Both"})
        
        # make sure that the default var and gene inheritance work
        self.assertTrue(self.inh.check_inheritance_mode_matches_gene_mode())
        
        # check that no gene inheritance overlap fails
        self.inh.gene_inheritance = {"Mosaic"}
        self.inh.inheritance_modes = {"Monoallelic", "Biallelic", "Both"}
        self.assertFalse(self.inh.check_inheritance_mode_matches_gene_mode())
        
        # check that a single inheritance type still works
        self.inh.gene_inheritance = {"Monoallelic"}
        self.assertTrue(self.inh.check_inheritance_mode_matches_gene_mode())
        
        # check that multiple inheritance types for a gene still work
        self.inh.gene_inheritance = {"Monoallelic", "Biallelic"}
        self.assertTrue(self.inh.check_inheritance_mode_matches_gene_mode())
        
        # check that extra inheritance modes are included still work
        self.inh.gene_inheritance = {"Monoallelic", "Biallelic", "Mosaic"}
        self.assertTrue(self.inh.check_inheritance_mode_matches_gene_mode())
    
    def test_set_trio_genotypes(self):
        """ test that set_trio_genotypes() works correctly
        """
        
        # set the genotypes using the default variant
        var = self.variants[0]
        self.inh.set_trio_genotypes(var)
        
        # the genotypes for the inh object should match the vars genotypes
        self.assertEqual(self.inh.child, var.child)
        self.assertEqual(self.inh.mom, var.mother)
        self.assertEqual(self.inh.dad, var.father)
        
        # now remove the parents before re-setting the genotypes
        del var.mother
        del var.father
        self.inh.trio.father = None
        self.inh.trio.mother = None
        self.inh.set_trio_genotypes(var)
        
        # the child should match the vars genotypes, but the parent's 
        # genotypes should be None
        self.assertEqual(self.inh.child, var.child)
        self.assertIsNone(self.inh.mom)
        self.assertIsNone(self.inh.dad)
    
    def test_add_variant_to_appropriate_list(self):
        """ test that add_variant_to_appropriate_list() works correctly
        """
        
        var = self.variants[0]
        inheritance = "Monoallelic"
        check = "compound_het"
        
        # check that compound_het vars are only added to the compound_het list
        self.inh.compound_hets = []
        self.inh.candidates = []
        self.inh.add_variant_to_appropriate_list(var, check, inheritance)
        self.assertEqual(self.inh.candidates, [])
        self.assertEqual(self.inh.compound_hets, [[var, check, inheritance]])
        
        # check that hemizygous vars are only added to the compound_het list
        self.inh.compound_hets = []
        self.inh.candidates = []
        check = "hemizygous"
        self.inh.add_variant_to_appropriate_list(var, check, inheritance)
        self.assertEqual(self.inh.candidates, [])
        self.assertEqual(self.inh.compound_hets, [[var, check, inheritance]])
        
        # check that single_variant vars are only added to the candidates list
        self.inh.compound_hets = []
        self.inh.candidates = []
        check = "single_variant"
        self.inh.add_variant_to_appropriate_list(var, check, inheritance)
        self.assertEqual(self.inh.candidates, [[var, check, inheritance]])
        self.assertEqual(self.inh.compound_hets, [])
        
        # check that other vars aren't added either list
        self.inh.compound_hets = []
        self.inh.candidates = []
        check = "nothing"
        self.inh.add_variant_to_appropriate_list(var, check, inheritance)
        self.assertEqual(self.inh.candidates, [])
        self.assertEqual(self.inh.compound_hets, [])
    
    # def test_check_compound_hets(self):
    #     """ test that check_compound_hets() works correctly
    #     """
        
    #     pass


# unittest.main()

