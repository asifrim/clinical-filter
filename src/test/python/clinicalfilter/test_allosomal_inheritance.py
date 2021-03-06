""" unit testing of the Allosomal class
"""


import unittest
from clinicalfilter.ped import Family
from clinicalfilter.variant.cnv import CNV
from clinicalfilter.variant.snv import SNV
from clinicalfilter.inheritance import Allosomal
from clinicalfilter.trio_genotypes import TrioGenotypes


class TestAllosomalPy(unittest.TestCase):
    """ test the Allosomal class
    """
    
    def setUp(self):
        """ define a family and variant, and start the Allosomal class
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
        
        self.inh = Allosomal(self.variants, self.trio, gene_inh)
        self.inh.is_lof = var.child.is_lof()
    
    def create_snv(self, gender, genotype):
        """ create a default variant
        """
        
        chrom = "X"
        pos = "15000000"
        snp_id = "."
        ref = "A"
        alt = "G"
        filt = "PASS"
        
        # set up a SNV object, since SNV inherits VcfInfo
        var = SNV(chrom, pos, snp_id, ref, alt, filt)
        
        info = "HGNC=TEST;CQ=missense_variant;random_tag"
        format_keys = "GT:DP"
        sample_values = genotype + ":50"
        
        var.add_info(info)
        var.add_format(format_keys, sample_values)
        var.set_gender(gender)
        var.set_genotype()
        
        return var
        
    def create_cnv(self, gender, inh, chrom, pos):
        """ create a default variant
        """
        
        snp_id = "."
        ref = "A"
        alt = "<DUP>"
        filt = "PASS"
        
        # set up a SNV object, since SNV inherits VcfInfo
        var = CNV(chrom, pos, snp_id, ref, alt, filt)
        
        info = "HGNC=TEST;HGNC_ALL=TEST;END=16000000;SVLEN=5000"
        format_keys = "INHERITANCE:DP"
        sample_values = inh + ":50"
        
        var.add_info(info)
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
    
    def set_trio_genos(self, var, geno):
        """ convenience function to set the trio genotypes for a variant
        """
        
        genos = {"0": "0/0", "1": "0/1", "2": "1/1"}
        
        # convert the geno codes to allele codes
        child = genos[geno[0]]
        mom = genos[geno[1]]
        dad = genos[geno[2]]
        
        # set the genotype field for each individual
        var.child.format["GT"] = child
        var.mother.format["GT"] = mom
        var.father.format["GT"] = dad
        
        # and set th genotype for each individual
        var.child.set_genotype()
        var.mother.set_genotype()
        var.father.set_genotype()
        
        # set the trio genotypes for the inheritance object
        self.inh.set_trio_genotypes(var)
    
    def test_check_variant_without_parents_female(self):
        """ test that check_variant_without_parents() works correctly for female
        """
        
        var = self.variants[0]
        var.child.set_gender("F")
        self.set_trio_genos(var, "100")
        
        # remove the parents, so it appears the var lacks parental information
        self.inh.trio.mother = None
        self.inh.trio.father = None
        
        # check for X-linked dominant inheritance
        self.assertEqual(self.inh.check_variant_without_parents("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "allosomal without parents")
        
        self.set_trio_genos(var, "200")
        self.assertEqual(self.inh.check_variant_without_parents("X-linked dominant"), "single_variant")
        
        # and check for hemizygous inheritance
        self.set_trio_genos(var, "100")
        self.assertEqual(self.inh.check_variant_without_parents("Hemizygous"), "hemizygous")
        
        self.set_trio_genos(var, "200")
        self.assertEqual(self.inh.check_variant_without_parents("Hemizygous"), "single_variant")
    
    def test_check_variant_without_parents_male(self):
        """ test that check_variant_without_parents() works correctly for males
        """
        
        var = self.variants[0]
        var.child.set_gender("M")
        self.set_trio_genos(var, "200")
        
        # remove the parents, so it appears the var lacks parental information
        self.inh.trio.mother = None
        self.inh.trio.father = None
        
        # check for X-linked dominant inheritance
        self.assertEqual(self.inh.check_variant_without_parents("X-linked dominant"), "single_variant")
        
        # and check for hemizygous inheritance
        self.assertEqual(self.inh.check_variant_without_parents("Hemizygous"), "single_variant")
    
    def test_check_heterozygous_de_novo(self):
        """ test that check_heterozygous() works correctly for de novos
        """
        
        # all of these tests are run for female X chrom de novos, since male
        # X chrom hets don't exist
        var = self.variants[0]
        self.set_trio_genos(var, "100")
        
        # check for X-linked dominant inheritance
        self.assertEqual(self.inh.check_heterozygous("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "female x chrom de novo")
        
        # check for biallelic inheritance
        self.assertEqual(self.inh.check_heterozygous("Hemizygous"), "single_variant")
        
        with self.assertRaises(ValueError):
            self.inh.check_heterozygous("X-linked over-dominance")
        
        for geno in ["102", "110", "112", "122"]:
            self.set_trio_genos(var, geno)
            self.inh.check_heterozygous("X-linked dominant")
            self.assertNotEqual(self.inh.log_string, "female x chrom de novo")
        
    def test_check_heterozygous_affected_mother(self):
        """ test that check_heterozygous() works correctly for affected mothers
        """
        
        var = self.variants[0]
        
        # check that trio = 110, with het affected mother is captured
        self.set_trio_genos(var, "110")
        self.inh.mother_affected = True
        self.assertEqual(self.inh.check_heterozygous("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "x chrom transmitted from aff, other parent non-carrier or aff")
        
        # check that when the other parent is also non-ref, the variant is no
        # longer captured, unless the parent is affected
        self.set_trio_genos(var, "112")
        self.assertEqual(self.inh.check_heterozygous("X-linked dominant"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
        
        self.inh.father_affected = True
        self.inh.check_heterozygous("X-linked dominant")
        self.assertEqual(self.inh.log_string, "x chrom transmitted from aff, other parent non-carrier or aff")
        
        # and check that hemizgygous vars return as "compound_het"
        self.assertEqual(self.inh.check_heterozygous("Hemizygous"), "compound_het")
    
    def test_check_heterozygous_affected_father(self):
        """ test that check_heterozygous() works correctly for affected fathers
        """
        
        var = self.variants[0]
        
        # set the father as non-ref genotype and affected
        self.set_trio_genos(var, "102")
        
        # check that the het proband, with het unaffected father is passes
        self.assertEqual(self.inh.check_heterozygous("X-linked dominant"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
        
        # check that the het proband, with het affected father is captured
        self.inh.father_affected = True
        self.assertEqual(self.inh.check_heterozygous("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "x chrom transmitted from aff, other parent non-carrier or aff")
        
        # check that when the other parent is also non-ref, the variant is no
        # longer captured, unless the parent is affected
        self.set_trio_genos(var, "112")
        self.assertEqual(self.inh.check_heterozygous("X-linked dominant"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
        
        self.inh.mother_affected = True
        self.inh.check_heterozygous("X-linked dominant")
        self.assertEqual(self.inh.log_string, "x chrom transmitted from aff, other parent non-carrier or aff")
    
    def test_check_homozygous_male(self):
        """ test that check_homozygous() works correctly for males
        """
        
        var = self.variants[0]
        self.trio.child.gender = "M"
        
        # check for trio = 200, which is de novo on male X chrom
        self.set_trio_genos(var, "200")
        self.assertEqual(self.inh.check_homozygous("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "male X chrom de novo")
        
        # check for trio = 210, with unaffected mother
        self.set_trio_genos(var, "210")
        self.assertEqual(self.inh.check_homozygous("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "male X chrom inherited from het mother or hom affected mother")
        
        # check for trio = 210, with affected mother, which should not pass
        self.inh.mother_affected = True
        self.assertEqual(self.inh.check_homozygous("X-linked dominant"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
        
        # check for trio = 220, with affected mother
        self.set_trio_genos(var, "220")
        self.assertEqual(self.inh.check_homozygous("X-linked dominant"), "single_variant")
        self.assertEqual(self.inh.log_string, "male X chrom inherited from het mother or hom affected mother")
        
        # check for trio = 220, with unaffected mother, which should not pass
        self.set_trio_genos(var, "220")
        self.inh.mother_affected = False
        self.assertEqual(self.inh.check_homozygous("X-linked dominant"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
        
        # check that non-standard inheritance modes raise errors
        with self.assertRaises(ValueError):
            self.inh.check_homozygous("X-linked over-dominance")
    
    def test_check_homozygous_female(self):
        """ test that check_homozygous() works correctly for females
        """
        
        var = self.variants[0]
        
        # check for trio = 200, which is non-mendelian
        self.set_trio_genos(var, "200")
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "nothing")
        self.assertEqual(self.inh.log_string, "non-mendelian trio")
        
        # check for trio = 210, which is non-mendelian
        self.set_trio_genos(var, "210")
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "nothing")
        self.assertEqual(self.inh.log_string, "non-mendelian trio")
        
        # check for trio = 202, which is non-mendelian
        self.set_trio_genos(var, "202")
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "nothing")
        self.assertEqual(self.inh.log_string, "non-mendelian trio")
        
        # and check for trio = 212, without affected parents
        self.set_trio_genos(var, "212")
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
        
        # and check for trio = 212, with affected father
        self.set_trio_genos(var, "212")
        self.inh.father_affected = True
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "single_variant")
        self.assertEqual(self.inh.log_string, "testing")
        
        # and check for trio = 212, with affected mother
        self.set_trio_genos(var, "212")
        self.inh.mother_affected = True
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "single_variant")
        self.assertEqual(self.inh.log_string, "testing")
        
        # and check for trio = 222, with affected mother
        self.set_trio_genos(var, "222")
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "single_variant")
        self.assertEqual(self.inh.log_string, "testing")
        
        # and check for trio = 222, with affected mother
        self.set_trio_genos(var, "222")
        self.inh.mother_affected = False
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "nothing")
        self.assertEqual(self.inh.log_string, "variant not compatible with being causal")
    
    def test_check_homozygous_with_cnv(self):
        """ test that check_homozygous() works correctly for variant lists with CNVs
        """
        
        # generate a test variant
        chrom = "X"
        position = "60000"
        child_var = self.create_cnv("F", "unknown", chrom, position)
        mom_var = self.create_cnv("F", "unknown", chrom, position)
        dad_var = self.create_cnv("M", "unknown", chrom, position)
        
        cnv_var = TrioGenotypes(child_var)
        cnv_var.add_mother_variant(mom_var)
        cnv_var.add_father_variant(dad_var)
        
        var = self.variants[0]
        
        # check for trio = 200, which is non-mendelian
        self.set_trio_genos(var, "200")
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "nothing")
        self.assertEqual(self.inh.log_string, "non-mendelian trio")
        
        # check when a CNV is in the variants list
        self.inh.variants.append(cnv_var)
        self.assertEqual(self.inh.check_homozygous("Hemizygous"), "compound_het")
        self.assertEqual(self.inh.log_string, "non-mendelian, but CNV might affect call")


if __name__ == '__main__':
    unittest.main()
