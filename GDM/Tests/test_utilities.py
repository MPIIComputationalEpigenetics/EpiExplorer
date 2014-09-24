""" utilites.py tests """

import os, os.path, sys, unittest


#nosetest will not add dir to path if it is a package(__init__.py)
#so add it explicitly

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:
    sys.path = [os.path.abspath(os.path.dirname(__file__) + "/..")] + sys.path

#Let's forget nosetests for now as the path sys.path setting is causing import errors:
#Failure: ImportError (No module named settings) ... ERROR
#
#======================================================================
#ERROR: Failure: ImportError (No module named settings)
#----------------------------------------------------------------------
#Traceback (most recent call last):
#  File "/usr/lib/python2.6/site-packages/nose/loader.py", line 364, in loadTestsFromName
#    addr.filename, addr.module)
#  File "/usr/lib/python2.6/site-packages/nose/importer.py", line 39, in importFromPath
#    return self.importFromDir(dir_path, fqname)
#  File "/usr/lib/python2.6/site-packages/nose/importer.py", line 84, in importFromDir
#    mod = load_module(part_fqname, fh, filename, desc)
#  File "/nfs/gns/homes/njohnson/src/git_repos/swingingsimian-EpiExplorer/GDM/utilities.py", line 12, in <module>
#    import settings
#ImportError: No module named settings
#
#----------------------------------------------------------------------
#Ran 1 test in 0.001s

#http://stackoverflow.com/questions/16174649/specially-named-directories-using-nosetests/16224909#16224909

import utilities
import settings

class test_utilities(unittest.TestCase):

    def setUp(self):
      #Create files and links in here
      #or do this in the tests so we can skip?
      #Need to check/set absentfile here and recreate if necessary
      #Change this to a Test subdir, so we can optionally keep the output?
      self.logfile     = os.path.abspath(os.path.dirname(__file__) + "/..") + "/test.log"
      settings.logFile = self.logfile
      pass

    def test_rmFiles_absent_file(self):
      #Raises exception
      #This raises actual Exception and fails if lamda is not used???
      self.assertRaises(Exception, lambda: utilities.rmFiles(["absentfile"], True))

      #No exception
      #This was causing failures as call to log defaults to a file which did not exist
      self.assertTrue(utilities.rmFiles(["absentfile"], False) == 0)

    def test_rmFiles_


    def tearDown(self):
      utilities.rmFiles([self.logfile], True)
      pass


#If we are just running this module directly, load the test suite and run.

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_utilities)
    unittest.TextTestRunner(verbosity=2).run(suite)
