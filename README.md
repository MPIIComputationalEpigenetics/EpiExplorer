# EpiExplorer

## Description

EpiExplorer is a web tool that allows you to use large reference epigenome datasets for your own analysis without complex scripting or laborous preprocessing

## How this repository is organized 

This repository contains the full EpiExplorer source code that is being used by EpiExplorer at MPI: [http://epiexplorer.mpi-inf.mpg.de](http://epiexplorer.mpi-inf.mpg.de)

* The Frontend folder contains the files that make the EpiExplorer front end as deployed on [http://epiexplorer.mpi-inf.mpg.de](http://epiexplorer.mpi-inf.mpg.de)
* The Backend folder contains the backend files responsible for preprocessing annotations, processing custom datasets and answering user queries
* The Datasets contain the information about genomic and epigenomic annotations used by EpiExplorer

## CompleteSearch

 CompleteSearch provides native support for advanced search features such as query autocompletion and database-style JOIN operations, and it has been shown to outperform more standard approaches based on inverted indices 

## Instalation guide:

### Backend installation

#### Necessary software:

* Linux or Mac Os X
* Python 2.6
* C++ Compiler
* [CompleteSearch](http://ad-wiki.informatik.uni-freiburg.de/completesearch) (See above)
* [BedTools](https://github.com/arq5x/bedtools2)

#### Installation

1. Install CompleteSearch [http://ad-wiki.informatik.uni-freiburg.de/completesearch](http://ad-wiki.informatik.uni-freiburg.de/completesearch)
2. Install bedtools [https://github.com/arq5x/bedtools2](https://github.com/arq5x/bedtools2)
3. Checkout EpiExplorer source code [https://github.com/MPIIComputationalEpigeNetics/EpiExplorer](https://github.com/MPIIComputationalEpigeNetics/EpiExplorer)
	* *UserInterface/* contains all userinterface files and is not relevant for this task.
	* *GDM/* contains all backend sources
	* *Datasets/* contains all dataset initialization settings
4. The backend sources have 3 main entry points:
	* *GDM/CGSDatasetServer.py* is the main dataset annotation server
	* *GDM/CGSQueryServer.py* is responsible for answering user queries and starting and stopping CompleteSearch instances
	* *GDM/CGSServer.py* is the main server used only to forward requests from the Userinterface
5. Set up EpiExplorer configuration file */Cosgen/GDM/settings.py*
	* Set up EpiExplorer path
	* Set up Bedtools path
	* Set up servers location addresses and ports
	* Set up completesearch path
	* Set up temporary files path

6. Start *CGSDatasetServer.py* 

7. Process the default region sets:
	* The *GDM/Tests/testServer.py* has the code of how to process the default regions

8. Start *CGSQueryServer.py* and *CGSServer.py*

### Frontend installation

#### Necessary software:

1. Apache HTTP server with [mod_python](http://modpython.org/)
2. Install Apache Httpd Server with PHP and mod_python
3. Configure Httpd server for handling the python files (.py) of the directory UserInterface/cgi-bin  with the mod_python module
4. Configure Httpd server for handling the PHP files (.php) of the directory UserInterface/www/pub
5. Configure the $rpc_server and $rpc_port variables inside the file UserInterface/www/pub/settings.php for pointing to CGSServer.py address and port


## Startup description

Upon starting the dataset server (*CGSDatasetServer.py*) performs the following actions:

1. Reads the available genome from the settings.py
2. For every genome, tries to read its basic initialization file
	1. These files are named unix_<genome>.ini and are located in the Datasets folder.
	2. Each line of this file is formed <dataset ID> = <path to dataset initilization file>
		1. Every dataset initialization file is of similar format <property> = <property value>
		2. The most important properties of each dataset initialization files are:
			* genome the genome assembly for the dataset
			* datasetSimpleName simple name for the dataset
			* datasetWordName name for the dataset used in words, it should be the same for similar properties across genomes
			* datasetPythonClass the class that handles similar types of data
			* hasFeatures if the dataset encodes features or not, for ex
			* hasGenomicRegions if the dataset encodes regions or not. For example the DNA sequence dataset has features, but does not have regions, while genome-wide tiling regions have regions, but do not have any annotation properties associated with them
			* These are only the common ones, for every specific dataset type there are other properties that are expected from the python classes for full customization
3. If a dataset requires downloading external resource, it is downloaded
4. If a dataset requires preprocessing, it is preprocessed
5. Some datasets should be downloaded before


## User Documentation
	
Tutorials are available at the [supplementary material page](http://epiexplorer.mpi-inf.mpg.de/supplementary/)

## How to cite EpiExplorer

Halachev, K., Bast, H., Albrecht, F., Lengauer, T. & Bock, C. EpiExplorer: live exploration and global analysis of large epigenomic datasets. Genome Biol. 13, R96 (2012). 

The paper is freely available at [http://genomebiology.com/2012/13/10/r96](http://genomebiology.com/2012/13/10/r96)

## References

Bast H, Weber I: The CompleteSearch engine: interactive, efficient, and
towards IR & DB integration. CIDR 2007, Third Biennial Conference on Innovative Data Systems Research: 7-10 January 2007; Asilomar, CA, USA 2007, 88-95, [proceedings](http://www.cidrdb.org/ 2007Proceedings.zip). [pdf](http://www.mpi-inf.mpg.de/~bast/papers/completesearch-cidr.pdf)
