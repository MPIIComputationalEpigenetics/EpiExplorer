# the regions are stored in a local file DB and the search structure is interval array

# This is a rehashing of BroadHistonesSingle.py
# Removing some of the hardcoding for custom formats and logic for tissue synonyms
# and adding some Histone defaults

# Either need to add back in the custom merged format support or force pre-processing outside this process.
# Currently this is all tied to starting up the CGSDatasetServer.

# This needs splitting up into a new base class and a Histone wrapper
# the base class will basically be a new version of DatasetRegionsWithTissues

# The config naming really needs overhauling, specifically around  the definition of the
# assay and the assayed feature, currently this is captured in various non-obvious ways
# e.g. datasetWordName = e.g. tfbs | bhist | DNaseI | rrbs all sorts of other werid stuff
#      FeatureType = H3K4me3 | P300 ?!! etc
#
# This can really be tied down to 3 values

# AssayType = RRBS | ChIP-Seq | DNase-Seq etc.
# FeatureType = 5mC | H3K4me3 | P300 | DNase1
# FeatureClass = DNAMethylation | Histone | TFBS | OpenChromatin

# Given these, there are also possible abbreviations at the class and feature type level
# The feature type abbreviations may in some cases come from the assay rather than the feature type
# e.g. it's arguably more sensible to use RRBS or WGBS rather than 5mC, as this is more informative and also
# does not overlook the fact the the BS-Seq tech cannot distinguish 5hmC

# Before this is change, need to validate where these vars are actually used, or just translate them
# appropriately in the data class sub class. Unfortunately FeatureType is used directly in the CGSDatasetServer
# Change in config and data set class, but maintain attr for compliance, or change CGSDatasetServer to use FeatureClass?

# All configs should expect tissues (can be singular)
# Add back in datasetFrom template suppor in getDownloadInfo? Probably not.
# Allow custom merged file integrating multiple tissues (i.e. no tissues config defined).
# Will either need to delegate to a parser or support this in the base class, based on a tissueIndex var

# BaseFeature? Can Features also have regions? Is there really any difference?
# DNase ChromHMM, enhanceers, cpg islangs and lamin_b1 all seems to use DatasetRegions(WithTissues)
# Not entirely sure exactly what the difference is in processing

# Regions specific
# useScore
# useStrand
# mergeOverlaps
# and a whole bunch of very similar code

# Let's concentrate on meth first, and see if we can integrate config/flow for DNase1 regions later
# Can Features also have regions?!!!!

import os
import os.path
import numpy  # Only required for numpy type definition
import sqlite3
import gzip
# import sys
import re
import warnings

from utilities import *
import Dataset
import IntervalArray
import settings

# todo NJ FeatureType is quite specific here, could this not be changed to feature_type?
# or can we use datasetOfficialName for now?
# todo Add support for various input formats, which would need implementing in the various
# functions which store/access data


class BaseFeature(Dataset.Dataset):
    # Note 'init' not a constructor!! Will have to be called explicitly
    # todo rename init?

    def __init__(self):
        Dataset.Dataset.__init__(self)
        # in 3.0 change this to super().__init__()

        # Some defaults
        self.hasFeatures = True
        # self.features = ['overlapBinary', 'overlapRatio', 'distanceToNearest']
        # Not sure features are actually ever used?
        # no reference to overlapBinary or distanceToNearest anywhere but config!
        # Apparently no reference to .features anywhere?
        # overlapRatio is hardcoded into several dataset classes?

        # These should really be set as lists but these are actually split in getDefaultAnnotationSettings
        # In fact there are many cases of attributes being split all over the place
        # These should move to init? Or preferably __init__ if readDataSet were to create these
        # properly by using kwargs with the following global default config
        # Or maybe this constructor should take a dictionary and handle params accordingly
        # http://code.activestate.com/recipes/438819-boring-constructor-pattern/
        # i.e. move the decorator into the base class, and pass through the
        # *kwargs along with the defaults in a ways that the *kwargs over-write the defaults
        # merge?

        # Can be over-ridden in subclasses, but tissue should always be first
        # due to list slice dependency in initializePropertiesComputeStructures
        # This should also match the calculate_insert_values function

        # todo need to make sure this format isn't propogated to the bed files
        self.feature_table_def = "(tissue TEXT, chrom INTEGER, start INTEGER, stop INTEGER)"

        # move this to a distance specific attr, and assign in subclass
        # could also enable 'decoration' based on data type in init
        self.annotated_table_def = "(regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, " + \
                                   "distance_upstream INTEGER, distance_downstream INTEGER)"
        # use this to dynamically define the word prefix keys?

        # Default bed values, they may not necessarily be used in the subclass
        # but they should be redefined if the format is not bed
        self.optional_suffix_regex = re.compile(r"(.*)(\.bb$)")
        self.is_half_open = 1  # Not boolean, as this will be used in calculation
        self.chromIndex = 0
        self.chromStartIndex = 1
        self.chromEndIndex = 2
        self.scoreIndex = 4
        self.scoreBase = 1000
        self.header_regex = re.compile("(track|#)")  # always from ^
        self.numpy_type = numpy.uint32
        # self.numpy_size = 2  # Now set dynamically in init
        # Should always be number of table fields - 2, as the interval array are tissue and chr specific
        # As these fields are ommitted, essentially these are just start and end values

        self.intervalArrays = {}
        self.FeatureType = None  # Define as string in subclass init

    def init(self, initCompute=True):
        # recast some ints if defaults have been over-ridden by custom ini values
        self.chromIndex = int(self.chromIndex)
        self.chromStartIndex = int(self.chromStartIndex)
        self.chromEndIndex = int(self.chromEndIndex)
        self.scoreIndex = int(self.scoreIndex)
        # what about recasting optional attributes i.e. anything ending in Index?

        if isinstance(self.tissues, str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))

        if isinstance(self.datasetFrom, str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))

        # NJ Removed datasetFrom templating support as was too project specific
        # No guarantee all sources would have the same url format
        # if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
        #    raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom))

        self.table_fields = re.sub("[\(\),]", "", self.feature_table_def).split(' ')[::2]
        self.param_sigils = "(" + ', '.join(len(self.table_fields) * ['?']) + ")"
        self.numpy_size = len(self.table_fields) - 2
        self.table_fields = ', '.join(self.table_fields)
        # warnings.warn("table fields are " + self.table_fields)
        # warnings.warn("param_sigils are " + self.param_sigils)

        # todo Need to validate some attrs have been set in the subclasses
        # This would normally be handled by a sensible __init__ constructor, sigh
        # self.FeatureType

        # This has to be last, as this actually start the processing and
        # above needs doing first (should really be in __init__!)
        Dataset.Dataset.init(self, initCompute)
        self.initialized = True

    # TODO Change this to support merged tissue format
    # TODO make this use attribs for format specific stuff
    # and revise converting optional files formats

    def getDownloadInfo(self, tissueIndex):
        if len(self.datasetFrom) > 1:
             datasetFrom = self.datasetFrom[tissueIndex]
        else:
            datasetFrom = self.datasetFrom[0]

        datasetURL = datasetFrom
        downloadedLastPart = os.path.basename(datasetURL)

        # Convert to .bed.gz from .bb
        # This will be done as part of downloadDataset
        # but probably should no be done from here at all
        # currently done by ProjectDatasetFetcher.py
        match_obj = self.optional_suffix_regex.match(downloadedLastPart)

        if match_obj:
            downloadedLastPart = re.sub(match_obj.group(2), ".bed.gz", downloadedLastPart)

        # todo NJ Really need a way to organise download area based on project and or data type
        # Could use datasetOfficialName for now?

        datasetLocalFile = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)


        # todo NJ This file may already have been converted from bb to bed and or gzipped
        # So we may no longer see it. We need to pass a reference to get local file path by source path
        # Or just implement bb support!
        return datasetURL, datasetLocalFile

    # TODO Change this to support merged tissue format, i.e. custom table

    def downloadDataset(self):  # format specific (actually just the bb/bed issue, which could be handled by a download wrapper/config?

        if self.hasAllDownloadedFiles():
            return

        # This is slightly redundant, we could easily nest download code in hasAllDownloadedFiles
        # and specify download=False kwarg
        # This would make calling this function more clear too
        # instead all calling downloadDataset (which may not download anything),
        # would call hasAllDownloadedFiles(download=True)
        # but downlaodDataset is called by the CGSDatasetServer, so cannot change

        for tissueIndex in range(len(self.tissues)):
            tissue = self.tissues[tissueIndex]
            datasetURL, datasetLocalFile = self.getDownloadInfo(tissueIndex)

            # NJ MD5 or add that to downloadFile ?!
            # could change this to getFile which would selectively wget or rsync
            # depending on the presence of data_root and ftp_root vars to use in datasetFrom replace


            if not os.path.isfile(datasetLocalFile):

                # Is this downloading the .bb as .bed!
                # Also not check about format here, it's just assuming!

                downloadFile(datasetURL, datasetLocalFile)
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " was downloaded"))
                #sys.exit("Need to implement bigBedToBed conversion here, downloaded file may be incorrectly name bed.gz when is still .bb")

                import subprocess
                ## cmd = "bigBedToBed " + datasetLocalFile + " " + datasetLocalFile + ".tmp"
                ## print cmd
                subprocess.call("bigBedToBed " + datasetLocalFile + " " + datasetLocalFile + ".tmp",  shell=True)
                subprocess.call("gzip -c " + datasetLocalFile + ".tmp > " + datasetLocalFile,  shell=True)
                subprocess.call("rm -f " + datasetLocalFile + ".tmp",  shell=True)

            else:
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " exists"))

            self.downloadUrls[tissue] = datasetURL
            self.downloadDate = fileTimeStr(datasetLocalFile)


    # TODO Change this to support merged tissue format

    def hasAllDownloadedFiles(self):
        # warnings.warn("In hasAllDownloadedFiles")

        # TODO These 3 if blocks should be done in __init__ (possibly Dataset)
        if isinstance(self.tissues,str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))

        if isinstance(self.datasetFrom,str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))

        if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
            raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom))


        for tissueIndex in range(len(self.tissues)):
            tissue = self.tissues[tissueIndex]
            datasetURL, datasetLocalFile = self.getDownloadInfo(tissueIndex)

            if os.path.isfile(datasetLocalFile):
                # warnings.warn("Found:\tx" + datasetLocalFile + "x")

                self.downloadUrls[tissue] = datasetURL
                self.downloadDate = fileTimeStr(datasetLocalFile)
            else:
                #warnings.warn("Local file could not be found.\n\tSource:\t" +
                #    datasetURL + "\n\tLocal:\t" + datasetLocalFile )

                # Probably don't want this here, but on the download instead
                # why is this  printing partial code?

                #if os.path.exists(datasetLocalFile):
                #    warnings.warn("But does exist")
                return False

        return True

    # This does currently not support anything but the BaseFeature default
    # annotations. If these have been redefined in a sublass, then this function
    # is updated it will have to be redefined in the subclass

    # Called by CGSDatasetServer.getGenomicRegionProperties and getGenomicRegionPropertiesForDataset
    # where is row from?
    # oddly both these set raw[0]/regionID field to -1?
    # Which is then subsequently propogated below in the result

    def computeSingleRegionProperties(self, row, cgsAS):
        # result will be self.annotation_table_def fields
        # e.g. regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER
        results = []
        isOfType = 0
        chrom = row[1]
        start = row[2]
        stop = row[3]
        strand = row[6]

        # The problem seems to be with a target set specific zip file
        # it seems like loading the chrom data

        # This is potentially unsafe as it depends on another initialise function being called first
        # That is only done in the context of the dataset server startup
        # These are only ever set in initializePropertiesComputeStructures, which then stores and purges the cached
        # data via cleanup
        # These are then loaded as required when processing regions of a query set
        # They are weakly tested on startup in the initialise function below

        # It seems to me that the level of re-use is at the sqlite DB, but that does not validate the number of records
        # (just the number of chroms?)
        # Could manage this by simply writing completely to tmp file first, then moving complete file to workign name
        # then test for file name.
        # Do we even need the sqlite DB after this stage, maybe not the main one regions DB, and maybe not the
        # 'feature' annotation DBs either? As they should ultimately be in a CS instance
        # The overlaps here are seemingly done with numpy, not bedtools?!
        # where is bedtools actually used?
        # bedtools are called directly rather than through bedtools wrapper e.g. sortBed rather than bedtools sort
        # merge, sort, annotated, closest. windowBed, shuffle seem to be the only ones used.
        # intersect is done here using numpy, using the chrom specific caches
        # This seems a bit crazy to be doing the intersect on a row by row basis
        # wouldn't it be faster to do it file by file
        # stream the input in and then do the rest of the processing in that loop?
        # this could even be threaded per tissue here to perform the overlaps

        # In fact it seems like these data processing operations should be moved to a separate class,
        # as there is massive redundancy across the dataset classes

        for tissue in self.intervalArrays.keys():
            # define_annoation_values can either be set to a code ref to
            # and existing function e.g. define_distance_annotation_values
            # or defined as a function in a subclass
            result = self.define_annotation_values(row, tissue,
                                                   cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue])

            # check for neighborhood
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
                positions = map(lambda x:start-x,cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodBeforeStart"))
                positions +=  map(lambda x:stop+x,cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodAfterEnd"))
                if strand == 1:
                    #minus strand reverse
                    positions.reverse()
                neighborhood = self.intervalArrays[tissue].findTwoDimentionalNeighborhood(chrom,positions)
                result.append(neighborhood)


            results.append(result)

        return results


    def define_annotation_values(self, row, tissue, tissue_data):
        raise Exception, ("define_annotation_values needs defining in a subclass" +
                          " or re-assigning to somethign like define_distance_annotation_values")


    def define_distance_annotation_values(self, row, tissue, tissue_data):
        chrom = row[1]
        start = row[2]
        stop = row[3]
        strand = row[6]
        overlapingRegions = self.intervalArrays[tissue].findTwoDimentionalWithAdditionalInfo(chrom, start, stop, tissue_data)
        overlap_count = len(overlapingRegions)
        result = []

        if overlap_count == 0:
            distance_upstream_array = tissue_data['distanceUpstream']
            distance_downstream_array = tissue_data['distanceDownstream']

            if strand == 1:
                #minus strand, reverse ???
                result = [row[0], 0, 0, distance_downstream_array, distance_upstream_array, tissue]
            else:
                result = [row[0], 0, 0, distance_upstream_array, distance_downstream_array, tissue]
        else:
            reducedGR = gr_reduceRegionSet(list(overlapingRegions))
            overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
            result = [row[0], overlap_ratio, overlap_count, 0, 0, tissue]

            if overlap_ratio < 0:
                raise GDMException, \
                    ("Negative overlap ratio " + str([str(row), self.FeatureType, tissue, overlap_count,
                                                      overlap_ratio, str(tissue_data), str(list(overlapingRegions))]))

        return result


    def define_insert_values(self, chrom, line, tissue):
        raise Exception, ("define_insert_values needs defining in a subclass" +
                          " or re-assigning to somethign like define_minimal_insert_values")


    def define_minimal_insert_values(self, chrom, line, tissue):
        # Should obviously match self.feature_table_def
        return tuple([tissue,
                      int(chrom),
                      int(line[self.chromStartIndex]) + self.is_half_open,
                      int(line[self.chromEndIndex])])



    # This is already quite generic, but we need to add support

    def preprocessDownloadedDataset(self):

        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText

        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            # NJ This is dangerous as the sqlite file may be incomplete or have old/corrupt data!!!!
            # TODO add validation and recovery modein here so we don't need to blow away the sqlite3 files all
            # the time
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in " + self.binaryFile
            log(extext)
            return

        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
        self.binaryFile = self.getDatasetBinaryName()

        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('CREATE TABLE ' + self.datasetSimpleName + self.feature_table_def)
            # NJ Not sure these are ever used but could be add score here?
            # self.signalValueIndex = int(self.signalValueIndex)
            # self.pValueIndex = int(self.pValueIndex)

            for tissueIndex in range(len(self.tissues)):
                tissue = self.tissues[tissueIndex]
                datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
                #print tissue,datasetLocalFile
                f = gzip.GzipFile(datasetLocalFile, "rb")
                lines = map(lambda x:x.strip().split("\t"), f.readlines())
                # Reading whole file in, then another iteration below?
                # only way to do header detection without a regex or test for every line
                f.close()
                # warnings.warn("Loading data for tissue:\t" + tissue)

                log("Loading " + tissue + " features from file:\t" + datasetLocalFile)

                # Detect header here first
                data_start_idx = 0

                for i in xrange(0,len(lines)):

                    if not self.header_regex.match(lines[i][0]):
                        data_start_idx = i
                        break


                for line in lines[data_start_idx:]:
                    try:
                        chrom = convertChromToInt(self.genome,line[self.chromIndex])
                    except:
                        if line[self.chromIndex] in ["_random", "chrM", "hap"]:
                            continue
                        elif line[self.chromIndex].startswith("chrUn"):
                            continue
                        else:
                            raise

                    c.execute("INSERT INTO " + self.datasetSimpleName + " VALUES " + self.param_sigils,
                              self.define_insert_values(chrom, line, tissue))


                conn.commit()

        except:
            # if there was exception, delete the database file
            c.close()
            conn.close()
            os.unlink(self.binaryFile)
            raise

        c.close()
        conn.close()
        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB " + self.binaryFile)


    def cleanup(self,cgsAS):
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
#        for tissue in self.intervalArrays.keys():
#            self.intervalArrays[tissue].cleanup()



    # TODO need to add single/NULL tissue support

    def initializePropertiesComputeStructures(self):
        log("Initializing interval arrays for " + self.FeatureType)
        chromData = {}
        chromSizes = {}
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()

        try:
            # initializing the IntervalArrays
            for tissueName in self.tissues:
                c.execute("SELECT COUNT(*) FROM " + self.datasetSimpleName + " WHERE tissue=? ORDER BY start", (tissueName,))
                nc = c.fetchone()[0]

                if nc == 0:
                    warnings.warn("Skipping IntervalArray:\t No " + tissueName + " features in " + self.binaryFile)
                    # NJ This will ultimately fail in when itertaing over the tissue in if len(data): below
                    # actually no, will just create empty lists for those tissues
                    # should prbably die here in some way? or at least warn about the absent data
                    continue

                self.intervalArrays[tissueName] = IntervalArray.GenomeIntervalArray(
                    self.getIntervalArraybaseName([tissueName]),
                    self.numpy_type,
                    self.numpy_size)


            self.intervalArrays["any"] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName(["any"]),
                                                                           self.numpy_type,
                                                                           self.numpy_size)
            exists = True
            # This does not test for partially loaded data! i.e. we should be matching nc versus the input data

            for tissue in self.intervalArrays.keys():

                # This appears to be the test for the chr specific zip file region caches
                # WTF testing random chr numbers?
                # The correct this to do here is to change the sql above to get the distinct list of chrom values
                # from the DB and test each one, or at least the last (assuming the order will always be preserved and correspond)
                # between that returned by sqlite and the order they are computed

                # Could go one further and load the numpy arrays to test the number of records
                # but if we implement the write to tmp first trick, then we can assume the content is complete
                # or at least as intended given the original source data.

                if self.intervalArrays[tissue].exist(1) and self.intervalArrays[tissue].exist(5) and self.intervalArrays[tissue].exist(11) and self.intervalArrays[tissue].exist(15):
                    continue
                else:
                    log(self.datasetSimpleName+" "+tissue+" has no stored computed array for some chromosomes")
                    exists = False
                    break

            if exists:
                log(self.datasetSimpleName+" have stored precomputed arrays")
                c.close()
                conn.close()
                return


            c.execute("SELECT " + self.table_fields +
                      " FROM " + self.datasetSimpleName + " ORDER BY chrom, start")
            data = c.fetchall()
        except:
            c.close()
            conn.close()
            raise

        c.close()
        conn.close()

        #log("MARK: all data was fetched")
        if len(data):

            # NJ These outer maps are just taking a copy of relevant part of data, but is this really necessary,
            # Filter provides a copy anyway and in the 2nd case it's just performing a shallow copy.
            # Couldn't the 2nd case be done more efficiently with data[:] (fastest) or list(data) (more readable)
            # both which shallow copy
            # The only reason to do this would be to protect against passing references which could be altered
            # or restrict the fields from the original data list. Neither is required here as all the fields are passed
            # the data is never altered in loadFullDataSortedbyChrom, so it would be safe/faster/more memory efficient
            # to pass references!
            # TODO Remove outer maps

            # Where is data actually set?
            # In fact, following loadFullDataSortedbyChrom it seems like data copying abounds using lambda and map
            # loadFullDataSortedbyChrom itself makes a copy of all the features per chrom (stripping the chrom field
            # before passing to addChromosomeArray
            # There is necessarily going to be some filtering based on tissue adn removeInclusion
            # but this could be done once instead of twice, this would remove an iteration and a copy of the data.

            # This would be much more efficient if done all in one method, and is the likely candidate for the
            # slow start initial start up

            # The data is ultimately set in the tissue specific IntervalArray.chroms[chrom] as a numpy array
            # So this is just start, end info as the chr info has been omited

            # When processing query feature ultimate IntervalArray.load is called via computeSingleRegionProperties
            #

            # This range should be numpy_size + 1
            # which is effectively the number of fields we want to store
            # minus tissue
            # we actually want to omit the tissue field form this data
            # Having it sat in the middle is slightly problematic
            # alternative is to always load tissue first?
            # itertools.chain may be useful here

            for tissue in self.tissues:
                # NJ tissueData = map(lambda x:x[:5],filter(lambda x:x[5]==tissue,data))
                tissueData = map(lambda x:x[1:],filter(lambda x:x[0]==tissue, data))
                self.intervalArrays[tissue].loadFullDataSortedbyChrom(tissueData,True)
                log("\ttissue " + tissue + " is ready")
            #log(["Adding an array for histone mark",hmark,"and tissue all with total of",len(data),"rows"])
            # NJ self.intervalArrays["any"].loadFullDataSortedbyChrom(map(lambda x:x[:5],data),True)

            # what is this map doing?
            # Is this just making a copy?

            # thsi probably needs modifying to integrate any additional data, such as signalValue for methylation?

            self.intervalArrays["any"].loadFullDataSortedbyChrom(map(lambda x:x[1:],data),True)
            log("\ttissue any is ready")

        log("Interval array computed for " + self.FeatureType)

        for tissue in self.intervalArrays.keys():
            # WTF!!! Double store!
            #self.intervalArrays[tissue].store()
            self.intervalArrays[tissue].cleanup()  # This also stores


        log("Interval array stored for " + self.FeatureType)


    # But can we maintain this, as will only be called if config is set appropriately?

    def calculateCoverages(self):  # Histone specific
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()

        try:
            for tissueName in self.tissues:
                c.execute("SELECT chrom, start, stop FROM " + self.datasetSimpleName +
                          " WHERE tissue=? ORDER BY chrom, start", (tissueName,))
                data = c.fetchall()
                # TODO workaround because the calculateCoverage uses numpy array.
                coverage = self.calculateCoverage(numpy.asarray(data))
                self.coverages[tissueName] = coverage

            c.execute("SELECT chrom, start, stop FROM " + self.datasetSimpleName + " ORDER BY chrom, start")
            data = c.fetchall()
            # TODO workaround because the calculateCoverage uses numpy array.
            coverage = self.calculateCoverage(numpy.asarray(data))
            self.coverages["any"] = coverage

        except:
            c.close()
            raise


    # Only releveant for hasRegions = True
    # def getRegions(self):
    #    return self.getRegionsFromLocalDB()



    # no indexes? Would speed up tissue based queries
    # probably better to add index after load for speed

    def initializePropertiesStoreStructures(self,cgsAS, dataConnections):
        annotation_table_def = self.annotated_table_def

        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName, 'useNeighborhood'):
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data " +
                                          re.sub("\)", ", neighborhood TEXT)", annotation_table_def ))
        else:  # no neighborhood
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data " +
                                          annotation_table_def)


    # This differs to Regions classes

    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT, neighborhood TEXT (depending on useNeighborhood)

        # NJ This is likely now
        # regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, neighborhood TEXT (depending on useNeighborhood)

        regionData = []
        regionDataWithScores = []

        # why are we doing str(result[5]),
        # this is the tissue, so already a string?
        # todo test removal of str on result[5] usage

        if result[2] > 0:
            # indicates that the regions overlaps with DNaseI hypersensitive site
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,self.FeatureType,str(result[5])])
            if result[1] >= 0.1:
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,self.FeatureType,str(result[5])])
            if result[1] >= 0.5:
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,self.FeatureType,str(result[5])])

            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,self.FeatureType,str(result[5]),wordFloat(result[1],2)])

        else:
            #the region does not overlap with a site, report distance to the nearest (not tissue specific)
            if str(result[5]) == "any":
                if result[4] < settings.MAX_DISTANCE:
                    dd  = wordMagnitude(result[4])
                    regionData.append([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,str(self.FeatureType),dd])
                if result[3] < settings.MAX_DISTANCE:
                    du  = wordMagnitude(result[3])
                    regionData.append([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,str(self.FeatureType),du])
                if result[4] < result[3]:
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.FeatureType),dd])
                elif result[3] < result[4]:
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.FeatureType),du])
                elif result[3] < settings.MAX_DISTANCE:
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.FeatureType),du])
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            index = 0
            # Neighborhood is demanded and computed for this dataset
            beforeStart =  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodBeforeStart")
            for i in xrange(len(beforeStart)):
                # NJ if result[8][i] == "1":
                if result[6][i] == "1":
                    regionData.append([settings.wordPrefixes["neighborhood"],
                                       self.datasetWordName,
                                       self.FeatureType,
                                       str(result[5]),
                                       "bs"+str(beforeStart[i])])
            bsl = len(beforeStart)
            afterEnd =  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodAfterEnd")
            for j in xrange(len(afterEnd)):
                # NJ if result[8][j+bsl] == "1":
                if result[6][j+bsl] == "1":

                    regionData.append([settings.wordPrefixes["neighborhood"],
                                   self.datasetWordName,
                                   self.FeatureType,
                                   str(result[5]),
                                   "ae"+str(afterEnd[j])])


        return regionData,regionDataWithScores

    # This differs to Regions classes

    def getWordPrefixes(self,cgsAS):
        wordPrefixes =  [
            settings.wordPrefixes["overlap"],
            settings.wordPrefixes["overlap10p"],
            settings.wordPrefixes["overlap50p"],
            ":".join([settings.wordPrefixes["overlapRatio"], self.datasetWordName, self.FeatureType]),
            ":".join([settings.wordPrefixes["minimumDistanceDownstream"], self.datasetWordName, self.FeatureType]),
            ":".join([settings.wordPrefixes["minimumDistanceUpstream"], self.datasetWordName, self.FeatureType]),
            ":".join([settings.wordPrefixes["minimumDistance"], self.datasetWordName, self.FeatureType])]

        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            wordPrefixes.append(":".join([settings.wordPrefixes["neighborhood"],self.datasetWordName,self.FeatureType]))
        return wordPrefixes


    def getWordsDescription(self):
        # NJ ???

        doc = []
        # for tissue in self.tissues:
        #    pass
        return doc


    # NJ awful lot of redundancy in here
    # There are also translations from the config to the dataset_info cache in CGSDatasetServer
    # Shouldn't most of this conversion be done in init? (assuming that is always called after readDataset
    # Wouldn't the best way be to use kwargs when creating the Dataset in readDataset
    # Convert 'True' to True there (instead of in the __init__ methods)
    # Then wouldn't need to call init separately and could rely on __init__ to do all that
    # validation and conversion
    # Can't do this as it impacts on the rest of the Dataset classes!

    def getDefaultAnnotationSettings(self):
        # obtain the default settings
        settingsLocal = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type
        settingsLocal["hasGenomicRegions"] = self.hasGenomicRegions
        settingsLocal["hasFeatures"] = self.hasFeatures
        if isinstance(self.useNeighborhood,str):
            self.useNeighborhood = self.useNeighborhood == "True"
        settingsLocal["useNeighborhood"] = self.useNeighborhood

        #neighborhood is to be used, so chekc the defined distances
        # initializing distances before the start
        settingsLocal["neighborhoodBeforeStart"] = self.neighborhoodBeforeStart.strip().split(",")
        #if none make sure there is no '' artifact from the split()
        if len(settingsLocal["neighborhoodBeforeStart"]) == 1 and not settingsLocal["neighborhoodBeforeStart"][0]:
              settingsLocal["neighborhoodBeforeStart"] = []
        # convert them all to ints
        settingsLocal["neighborhoodBeforeStart"] = map(int,settingsLocal["neighborhoodBeforeStart"])

        # initializing distances after the end
        settingsLocal["neighborhoodAfterEnd"] = self.neighborhoodAfterEnd.strip().split(",")
        #if none make sure there is no '' artifact from the split()
        if len(settingsLocal["neighborhoodAfterEnd"]) == 1 and not settingsLocal["neighborhoodAfterEnd"][0]:
              settingsLocal["neighborhoodAfterEnd"] = []
        # convert them all to ints
        settingsLocal["neighborhoodAfterEnd"] = map(int,settingsLocal["neighborhoodAfterEnd"])

        settingsLocal["data"] = {}
        for tissue in self.tissues+['any']:
            settingsLocal["data"][tissue] = {'distanceDownstream':settings.MAX_DISTANCE,
                            'distanceUpstream':settings.MAX_DISTANCE,
                            'currentChrom':None,
                            'currentChromStart': 0,
                            'currentStartIndex':None,
                            'currentEndIndex':None}

        #retrun them
        return settingsLocal

    # This method returns a list of feature words for the feature listing in the user interface
    def getVisualizationFeatures(self,annotationFeatures):
        categories = self.dataCategories.strip()
        if len(categories) == 0:
            categoriesPath = [self.datasetSimpleName]
        else:
            categoriesPath = map(lambda x:x.strip(),categories.split("/"))+[self.datasetSimpleName]
        featureWords = []

        # NJ What do Emdd, Emud, Emmd, Enbh, Eor and POS3SOP and ::2::0 mean?
        # "minimumDistance": "Emmd",
        # "minimumDistanceUpstream": "Emud",
        # "minimumDistanceDownstream": "Emdd",
        # "overlapRatio": "Eor",
        # "neighborhood": "Enbh",
        # POS3SOP does not appear anywhere in the rest of the code base

        # why no tissue specificity here?
        # datasetWordName for BroadHistones was just bhist?
        # so the tissue spcificity must be done in the caller
        # which must be in this class?

        # From the CGSTexts word format it looks like it should appear after FeatureType
        # which may explain the ::, but then it would appear the DNAMethylation is wrong as this
        # includes tissue, but also has "::2::0"


        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+":"+self.FeatureType+"::"+"Eor:"+self.datasetWordName+":"+self.FeatureType+":POS3SOP::2::0"])
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName+":"+self.FeatureType])

        featureWords.append(categoriesPath+["distanceTo"]+["Emdd:"+self.datasetWordName+":"+self.FeatureType+"::2::0"])
        featureWords.append(categoriesPath+["distanceTo"]+["Emud:"+self.datasetWordName+":"+self.FeatureType+"::2::0"])
        featureWords.append(categoriesPath+["distanceTo"]+["Emmd:"+self.datasetWordName+":"+self.FeatureType+"::2::0"])

        if annotationFeatures["useNeighborhood"]:
            bsN = ":".join(map(str,annotationFeatures["neighborhoodBeforeStart"]))
            aeN = ":".join(map(str,annotationFeatures["neighborhoodAfterEnd"]))
            featureWords.append(categoriesPath+["Enbh:"+self.datasetWordName+":"+self.FeatureType+"::"+bsN+"::"+aeN])
        return featureWords

    # The rest of this class is written assuming overlap/distance data
    # but here we are ommiting as this would result in having to redefine this
    # as a pass method in non-overlap/distance subclasses
    # This is slightly unsafe, as subclasses may not implement some methods
    # we could always define the functions as code ref attrs
    # these would then be set in the subclass init
    # allowing code to be shared in this base class without
    # Then simply defining the default functions in sublasses
    # would overide this deffault core ref redirection
    # as per define_annotation_values
    # This will only work for this which will be redefined
    # not for the case below
    # This is only useful if we don't want to define intermediary classes to
    # hold the shared common code.
    # but that would be better if there are a bunch of related methods
    # which there seems to be

    # def getOverlappingText(self):
    #    return self.datasetWordName + ":" + self.FeatureType

    def getSubAnnotations(self):
        return self.tissues+["any"]
