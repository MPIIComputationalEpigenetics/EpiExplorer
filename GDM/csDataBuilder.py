import os
import subprocess

import utilities
import settings

# TODO: Log it.
# TODO: use settings.py
class CSDataBuilder:
    def __init__(self, path, name):
        self.__buildIndex = settings.buildIndex
        self.__buildDocsDB = settings.buildDocsDB
        self.__path = path
        self.__db = name
        self.__sorted_file_path =  "%(path)s/%(db)s.words-sorted.ascii" % {"path": self.__path, "db": self.__db}

    def do_prefix_sort(self):        
        file_path =  "%(path)s/%(db)s.hybrid.prefixes" % {"path": self.__path, "db": self.__db}
	my_env = {}
	my_env["LC_ALL"]="POSIX"
        cmd = ["/bin/sort", "-b", "-k1,1", "-k2,2n", "-k4,4n", file_path]

        sorted_file_name = file_path + ".tmp"
        sorted_file = open(sorted_file_name, "w")
        
        px = subprocess.Popen(cmd, stdout=sorted_file, stderr=subprocess.PIPE, env=my_env)
        stderr = px.communicate()                    
        sorted_file.close()
        
        os.remove(file_path)
        os.rename(sorted_file_name, file_path)

        utilities.log_CDS("csDataBuilder do_sort: STDERR: "+str(stderr))
        
    def do_sort(self):
        file_path =  "%(path)s/%(db)s.words-unsorted.ascii" % {"path": self.__path, "db": self.__db}
        cmd = ["/bin/sort","-S4G","-T"+settings.fastTmpFolder,"-b", "-k1,1", "-k2,2n", "-k4,4n", file_path]

        sorted_file = open(self.__sorted_file_path, "w")
        my_env = {}
	my_env["LC_ALL"]="POSIX"


        px = subprocess.Popen(cmd, stdout=sorted_file, stderr=subprocess.PIPE, env=my_env)
        stderr = px.communicate()                    
        sorted_file.close()

        os.remove(file_path)

        utilities.log_CDS("csDataBuilder do_sort: STDERR: "+str(stderr))
        

    def do_build_index(self, delete_intermediary = True):
        prefixes = "%(path)s/%(db)s.hybrid.prefixes" % {"path": self.__path, "db": self.__db}
        output = "%(path)s/%(db)s.ANY_SUFFIX_WITHOUT_DOT" % {"path": self.__path, "db": self.__db}

        cmd = [self.__buildIndex, "-b", prefixes , "-f", "ASCII", "HYB", output]

        print cmd
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        utilities.log_CDS("csDataBuilder do_build_index: STDOUT: "+str(stdout))
        utilities.log_CDS("csDataBuilder do_build_index: STDERR: "+str(stderr))
       
        f = "%(path)s/%(db)s.hybrid" % {"path": self.__path, "db": self.__db}
        t = "%(path)s/%(db)s.hybrid.from-ascii.withprefixes" % {"path": self.__path, "db": self.__db}

        
        if os.path.exists(t):
            os.remove(t)
            
        os.symlink(f, t)


###########
# DOCS
###########
#/TL/epigenetics/work/completesearch/dev_codebase/codebase/server/buildDocsDB -f hg18_ucsc_cpg_islands.docs-sorted 
    def do_build_docs(self):
        docs_file = "%(path)s/%(db)s.docs-sorted" %{"path": self.__path, "db": self.__db}
        cmd = [self.__buildDocsDB, "-f", docs_file]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        utilities.log_CDS("csDataBuilder do_build_docs: STDOUT: "+str(stdout))
        utilities.log_CDS("csDataBuilder do_build_docs: STDERR: "+str(stderr))
        
        f = "%(path)s/%(db)s.docs-sorted.DB" %{"path": self.__path, "db": self.__db}
        t = "%(path)s/%(db)s.docs.DB" %{"path": self.__path, "db": self.__db}

        os.rename(f, t)
'''
Build data for complete search
'''
def buildCSData(path, db, delete_intermediary = True):
    nm = CSDataBuilder(path,db)
    nm.do_prefix_sort()
    nm.do_sort()
    nm.do_build_index(False)
    nm.do_build_docs()

# Just for testing
if __name__ == "__main__":
    path = "/home/albrecht/tools/Cosgen/Datasets/hg18_CSFiles.new/"
    db = "hg18_ucsc_cpg_islands"
    buildCSData(path, db)
