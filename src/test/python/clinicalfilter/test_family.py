""" unit testing of the Family class
"""

import unittest
from clinicalfilter.ped import Family


class TestFamily(unittest.TestCase):
    """
    """
    
    def setUp(self):
        """ define a default Person object
        """
        
        ID = "fam_ID"
        
        self.family = Family(ID)
    
    def test_add_father(self):
        """ test that add_father() works correctly
        """
        
        ID = "parent_ID"
        path = "/home/parent.vcf"
        affected = "1"
        gender = "1"
        
        # check that adding a male father doesn't raise an error
        self.family.add_father(ID, path, affected, gender)
        
        # check that adding a father for a second time is fine, but adding 
        # a different father raises an error
        self.family.add_father(ID, path, affected, gender)
        with self.assertRaises(ValueError):
            self.family.add_father("different_ID", path, affected, gender)
        
        # check that adding a female father raises an error
        self.setUp()
        gender = "2"
        with self.assertRaises(ValueError):
            self.family.add_father(ID, path, affected, gender)
        
    def test_add_mother(self):
        """ test that add_mother() works correctly
        """
        
        ID = "parent_ID"
        path = "/home/parent.vcf"
        affected = "1"
        gender = "2"
        
        # check that adding a female mother doesn't raise an error
        self.family.add_mother(ID, path, affected, gender)
        
        # check that adding a mother for a second time is fine, but adding 
        # a different mother raises an error
        self.family.add_mother(ID, path, affected, gender)
        with self.assertRaises(ValueError):
            self.family.add_mother("different_ID", path, affected, gender)
        
        # check that adding a male mother raises an error
        self.setUp()
        gender = "1"
        with self.assertRaises(ValueError):
            self.family.add_mother(ID, path, affected, gender)
        
    def test_add_child(self):
        """ check that add_child() works correctly
        """
        
        # check that we can add one child
        self.family.add_child("child1", "/home/child1.vcf", "2", "1")
        self.assertEqual(len(self.family.children), 1)
        
        # check that adding multiple children works correctly
        self.family.add_child("child2", "/home/child2.vcf", "2", "2")
        self.family.add_child("child3", "/home/child3.vcf", "2", "1")
        self.assertEqual(len(self.family.children), 3)
    
    def test_set_child(self):
        """ test that set_child() works correctly
        """
        
        # add one child
        self.family.add_child("child1", "/home/child1.vcf", "2", "1")
        
        # check that the child can be set correctly
        self.family.set_child()
        self.assertEqual(self.family.child, self.family.children[0])
    
        # add more children
        self.family.add_child("child2", "/home/child2.vcf", "2", "1")
        self.family.add_child("child3", "/home/child3.vcf", "2", "2")
        
        # check that the child can be set correctly with multiple children
        self.family.set_child()
        self.assertIn(self.family.child, self.family.children)
        
    
    def test_set_child_examined(self):
        """ test that set_child_examined() works correctly
        """
        
        # add one child
        self.family.add_child("child1", "/home/child1.vcf", "2", "1")
        
        # check that the child can be set correctly, and can be set as having
        # been examined
        self.family.set_child()
        self.family.set_child_examined()
        self.assertTrue(self.family.children[0].is_analysed())
        self.assertIsNone(self.family.child)
        
        # add another child, and check that when we set the child, we now pick
        # up this child since the other one has previously been examined
        self.family.add_child("child2", "/home/child2.vcf", "2", "2")
        self.family.set_child()
        self.assertEqual(self.family.child, self.family.children[1])
        
        # make sure that set_child_examined() doesn't default to None if we 
        # have children left to analyse
        self.family.add_child("child3", "/home/child3.vcf", "2", "2")
        self.family.set_child()
        self.family.set_child_examined()
        self.assertIsNotNone(self.family.child)
        
        # and set child = None once we have analysed all the children
        self.family.set_child()
        self.family.set_child_examined()
        self.assertIsNone(self.family.child)


if __name__ == '__main__':
    unittest.main()


