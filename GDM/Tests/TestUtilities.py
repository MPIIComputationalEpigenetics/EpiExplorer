""" utilites.py tests """

import os, os.path, unittest

# PYTHONPATH should be set up in environment

# nosetest will not add dir to path if it is a package(__init__.py)
# so add it explicitly

# Let's forget nosetests for now as the path sys.path setting is causing import errors:
# Failure: ImportError (No module named settings) ... ERROR
#
# ======================================================================
# ERROR: Failure: ImportError (No module named settings)
# ----------------------------------------------------------------------
# Traceback (most recent call last):
#  File "/usr/lib/python2.6/site-packages/nose/loader.py", line 364, in loadTestsFromName
#    addr.filename, addr.module)
#  File "/usr/lib/python2.6/site-packages/nose/importer.py", line 39, in importFromPath
#    return self.importFromDir(dir_path, fqname)
#  File "/usr/lib/python2.6/site-packages/nose/importer.py", line 84, in importFromDir
#    mod = load_module(part_fqname, fh, filename, desc)
#  File "/nfs/gns/homes/njohnson/src/git_repos/swingingsimian-EpiExplorer/GDM/utilities.py", line 12, in <module>
#    import settings
# ImportError: No module named settings
#
# ----------------------------------------------------------------------
# Ran 1 test in 0.001s
# http://stackoverflow.com/questions/16174649/specially-named-directories-using-nosetests/16224909#16224909

import utilities
import settings


class TestUtilities(unittest.TestCase):

    def setUp(self):
        # Create files and links in here
        # or do this in the tests so we can skip?
        # Need to check/set absentfile here and recreate if necessary
        # Change this to a Test subdir, so we can optionally keep the output?
        self.logfile = os.path.abspath(os.path.dirname(__file__) + "/..") + "/test.log"
        settings.logFile = self.logfile

    def test_rm_files_absent_file(self):
        # Raises exception
        # This raises actual Exception and fails if lamda is not used???
        # http://stackoverflow.com/questions/6103825/how-to-properly-use-unit-testings-assertraises-with-nonetype-objects
        self.assertRaises(Exception, lambda: utilities.rm_files(["absentfile"], True))

        # No exception
        # This was causing failures as call to log defaults to a file which did not exist
        self.assertTrue(utilities.rm_files(["absentfile"], False) == 0)

    def test_rm_files_success(self):
        pass

    def test_read_ini_file(self):
        pass

    def tearDown(self):
        utilities.rm_files([self.logfile], True)

# If we are just running this module directly, load the test suite and run.

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUtilities)
    unittest.TextTestRunner(verbosity=2).run(suite)