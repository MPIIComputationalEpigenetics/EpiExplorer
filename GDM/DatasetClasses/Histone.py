# the regions are stored in a local file DB and the search structure is inteval tree
import os
import os.path
import numpy
import sqlite3
import gc
import sys
import gzip
import os.path
import time


#Now handled by PYTHONPATH
#mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep
#sys.path.insert(0,mainFolder)

import re

from utilities import *
import Dataset
import IntervalArray
# import IntervalTree
import settings
# import cPickle
# import utilities


# todo NJ Move a lot of this out to a bed format file, or a Dataset methods which takes the relevant bed config
# todo NJ histoneMark is quite specific here, could this not be changed to feature_type? or can we use datasetOfficialName
# for now?


# todo Add support for variouw input formats, which would need implementing in the various functions which store/access data

suffix_regex = re.compile(r"(.*)(\.bb$)")

class Histone(Dataset.Dataset):

    # Note 'init' not a constructor!! Will have to be called explicitly
    # todo rename init?


    def __init__(self):
        Dataset.Dataset.__init__(self)
        # in 3.0 change this to super().__init__()

        # Some defaults
        self.hasFeatures = True
        #self.features = ['overlapBinary', 'overlapRatio', 'distanceToNearest']
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

        # where is Histone.init called? Not from readDatasetDescriptions.readDataSet!

        # Should also have some validation of the fields in Dataset.__init__
        # This should protect against mets characters creeping into sensitive attrs


        self.neighborhoodAfterEnd = '0,30,100,300,1000,3000,10000,30000,100000'
        self.neighborhoodBeforeStart = '100000,30000,10000,3000,1000,300,100,30,0'
        self.useNeighborhood = True  # Could drop this and simply test for above attrs



    def init(self, initCompute=True):
        self.intervalArrays = {}
        Dataset.Dataset.init(self,initCompute)

        # todo NJ move this to Dataset.init?
        if isinstance(self.tissues,str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))
        if isinstance(self.datasetFrom,str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))

        # NJ Removed datasetFrom templating support as was too project specific
        # No guarantee all sources would have the same url format
        # if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
        #    raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom))
        self.initialized = True


    def getDownloadInfo(self, tissueIndex):
        # todo NJ this should be in base Dataset class?

        tissue = self.tissues[tissueIndex]

        if len(self.datasetFrom) > 1:
             datasetFrom = self.datasetFrom[tissueIndex]
        else:
            datasetFrom = self.datasetFrom[0]

        # This looks like some attempt to have a single URL template for all tissues
        # It is however prone to name modifications as HSMMtube shows below
        # looks like this should have returned by now if len(self.datasetFrom) > 1:
        #
        # if tissue == "HSMMtube":
        #    thURL = datasetFrom.replace("TISSUE","Hsmmt")
        # else:
        #    thURL = datasetFrom.replace("TISSUE",tissue.capitalize())
        #
        # datasetURL = thURL.replace("HMOD",self.histoneMark.capitalize())
        datasetURL = datasetFrom
        downloadedLastPart = os.path.basename(datasetURL)

        # Convert to .bed.gz from .bb
        # This will be done as part of downloadDataset
        # but probably should no be done from here at all
        # currently done by ProjectDatasetFetcher.py
        match_obj = suffix_regex.match(downloadedLastPart)


        if match_obj:
            downloadedLastPart = re.sub(match_obj.group(2), ".bed.gz", downloadedLastPart)

        # todo NJ Really need a way to organise download area based on project and or data type
        # Could use datasetOfficialName for now?

        datasetLocalFile = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)


        # todo NJ This file may already have been converted from bb to bed and or gzipped
        # So we may no longer see it. We need to pass a reference to get local file path by source path
        # Or just implement bb support!


        return datasetURL, datasetLocalFile

    def downloadDataset(self):

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
            datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)

            # NJ MD5 or add that to downloadFile ?!
            # could change this to getFile which would selectively wget or rsync
            # depending on the presence of data_root and ftp_root vars to use in datasetFrom replace


            if not os.path.isfile(datasetLocalFile):
                downloadFile(datasetURL, datasetLocalFile)
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " was downloaded"))
                sys.exit("Need to implement bigBedToBed conversion here")
            else:
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " exists"))

            self.downloadUrls[tissue] = datasetURL
            self.downloadDate = fileTimeStr(datasetLocalFile)




    def hasAllDownloadedFiles(self):
        # warning("In hasAllDownloadedFiles")

        # TODO These 3 if blocks should be done in __init__ (possibly Dataset)
        if isinstance(self.tissues,str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))

        if isinstance(self.datasetFrom,str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))

        if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
            raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom))

        '''
        for fileIndex in range(len(self.datasetFrom)):
            datasetURL, lfile = self.getDownloadInfo(fileIndex)
            print "PRE Checking local file for:\t" + datasetURL

            if os.path.isfile(lfile):
                print "Found:\t" + lfile
            else:
                print "Absent:\t" + lfile
        '''


        for tissueIndex in range(len(self.tissues)):
            tissue = self.tissues[tissueIndex]
            datasetURL, datasetLocalFile = self.getDownloadInfo(tissueIndex)

            # NJ For some reason the final datasetLocalFile in this loop is never seen by isfile and returns False?

            if os.path.isfile(datasetLocalFile):
                # warning("Found:\tx" + datasetLocalFile + "x")

                self.downloadUrls[tissue] = datasetURL
                self.downloadDate = fileTimeStr(datasetLocalFile)
            else:
                warning("Not found as file:\tx" + datasetLocalFile + "x")

                # ls_output = os.popen('ls ' + datasetLocalFile).read()
                # warning("ls output is" + ls_output)
                '''
                items = os.path.split(datasetLocalFile)
                for i in range(1,len(items)):
                    path = items[0]

                    print "Testing path %s" % (path)
                    print "path var is a " + str(type(path))
                    if os.path.exists(path):
                        print 'Y'
                    else:
                        print 'N'
                '''

                #if os.path.exists(datasetLocalFile):
                #    warning("But does exist")
                return False

        return True

    def computeSingleRegionProperties(self, row, cgsAS):
        # regionID, overlap_ratio, overlap_count, distance_upstream, distance_downstream, tissue, histoneMark
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
C

        for tissue in self.intervalArrays.keys():
            overlapingRegions = self.intervalArrays[tissue].findTwoDimentionalWithAdditionalInfo(chrom, start, stop,cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue])
            overlap_count = len(overlapingRegions)

            if overlap_count == 0:
                distance_upstream_array = cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]['distanceUpstream']
                distance_downstream_array = cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]['distanceDownstream']
                if strand == 1:
                    #minus strand, reverse
                    # NJ result = [row[0], 0, 0, distance_downstream_array, distance_upstream_array, tissue, 0, 0]
                    result = [row[0], 0, 0, distance_downstream_array, distance_upstream_array, tissue]
                else:
                    # NJ result = [row[0], 0, 0, distance_upstream_array, distance_downstream_array, tissue, 0, 0]
                    result = [row[0], 0, 0, distance_upstream_array, distance_downstream_array, tissue]
            else:
                reducedGR = gr_reduceRegionSet(list(overlapingRegions))
                overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
                # NJ result = [row[0], overlap_ratio, overlap_count, 0, 0, tissue, 0, 0]
                result = [row[0], overlap_ratio, overlap_count, 0, 0, tissue]
                if overlap_ratio < 0:
                    raise GDMException,"Negative overlap ratio "+str([str(row),self.histoneMark,tissue,overlap_count,overlap_ratio,str(cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]),str(list(overlapingRegions))])

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


    def preprocessDownloadedDataset(self):
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed

            # NJ This is dangerous as the sqlite file may be incomplete or have old/corrupt data


            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.binaryFile
            log(extext)
            return
        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
        self.binaryFile = self.getDatasetBinaryName()
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            # NJ c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, tissue TEXT, signalValue FLOAT, pValue FLOAT)')
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, tissue TEXT)')


            self.chromIndex = int(self.chromIndex)
            self.chromStartIndex = int(self.chromStartIndex)
            self.chromEndIndex = int(self.chromEndIndex)

            # NJ Not sure these are ever used but could be add score here?
            # self.signalValueIndex = int(self.signalValueIndex)
            # self.pValueIndex = int(self.pValueIndex)

            for tissueIndex in range(len(self.tissues)):
                tissue = self.tissues[tissueIndex]
                datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
                #print tissue,datasetLocalFile
                f = gzip.GzipFile(datasetLocalFile,"rb")
                lines = map(lambda x:x.strip().split("\t"),f.readlines())
                # NJ Reading whole file in? then another iterating below
                f.close()


                # warning("Loading data for tissue:\t" + tissue)

                for line in lines:
                    try:
                        chrom = convertChromToInt(self.genome,line[self.chromIndex])
                    except:
                        if "_random" in line[self.chromIndex]:
                            continue
                        elif "chrM" in line[self.chromIndex]:
                            continue
                        elif "hap" in line[self.chromIndex]:
                            continue
                        elif line[self.chromIndex].startswith("chrUn"):
                            continue
                        else:
                            raise
                    c.execute('INSERT INTO ' + self.datasetSimpleName + ' VALUES (?,?,?,?)',
                                   tuple([chrom,
                                          int(line[self.chromStartIndex]),
                                          int(line[self.chromEndIndex]),
                                          tissue,
                                         # NJ float(line[self.signalValueIndex]),
                                         # NJ float(line[self.pValueIndex]),
                                          ]))
                conn.commit()

        except:
            # if there was exception, delete the database file
            c.close()
            conn.close()
            os.unlink(self.binaryFile)
            raise

        c.close()
        conn.close()
        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB "+self.binaryFile)

    def cleanup(self,cgsAS):
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
#        for tissue in self.intervalArrays.keys():
#            self.intervalArrays[tissue].cleanup()



    # todo NJ alter code to match bed format in here?

    def initializePropertiesComputeStructures(self):
        log("computing interval array for " + self.histoneMark)
        chromData = {}
        chromSizes = {}

        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        try:

            # NJ Might the reshape error be down to the arrayDimension value of 4?
            # This varies across Dataset classes
            # we can also probably change the type, as we're not even storing the pvalues anymore
            # was 4 the number of fields in the originaly numpy arrays? i.e.
            # start, stop,  signalValue, pValue
            # If so, then this shoudl all be done automatically based on some format config!!!
            # let's try this with 2
            # This should always be num table fields - 2


            # initializing the IntervalArrays
            for tissueName in self.tissues:
                c.execute("SELECT COUNT(*) FROM " + self.datasetSimpleName + " WHERE tissue=? ORDER BY start",(tissueName,))
                nc = c.fetchone()[0]

                if nc == 0:
                    warning("Skipping IntervalArray for " + tissueName)
                    # NJ This will ultimately fail in when itertaing over the tissue in if len(data): below
                    # actually no, will just create empty lists for those tissues
                    # should prbably die here in some way? or at least warn about the absent data
                    continue

                # NJ self.intervalArrays[tissueName] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([tissueName]),numpy.float64,4)
                self.intervalArrays[tissueName] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([tissueName]),numpy.uint32,2)

            # NJ self.intervalArrays["any"] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName(["any"]),numpy.float64,4)
            self.intervalArrays["any"] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName(["any"]),numpy.uint32,2)
            exist = True

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
                    exist = False
                    break

            if exist:
                log(self.datasetSimpleName+" have stored precomputed arrays")
                c.close()
                conn.close()
                return

            # NJ c.execute("SELECT chrom, start, stop,  signalValue, pValue, tissue FROM "+self.datasetSimpleName+" ORDER BY chrom,start")

            c.execute("SELECT chrom, start, stop, tissue FROM "+self.datasetSimpleName+" ORDER BY chrom, start")
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

            for tissue in self.tissues:
                # NJ tissueData = map(lambda x:x[:5],filter(lambda x:x[5]==tissue,data))
                tissueData = map(lambda x:x[:3],filter(lambda x:x[3]==tissue, data))
                self.intervalArrays[tissue].loadFullDataSortedbyChrom(tissueData,True)
                log("\ttissue " + tissue + " is ready")
            #log(["Adding an array for histone mark",hmark,"and tissue all with total of",len(data),"rows"])
            # NJ self.intervalArrays["any"].loadFullDataSortedbyChrom(map(lambda x:x[:5],data),True)

            # what is this map doing?
            # Is this just making a copy?


            self.intervalArrays["any"].loadFullDataSortedbyChrom(map(lambda x:x[:3],data),True)
            log("\ttissue any is ready")

        log("Interval array computed for " + self.histoneMark)

        for tissue in self.intervalArrays.keys():
            # WTF!!! Double store!
            #self.intervalArrays[tissue].store()
            self.intervalArrays[tissue].cleanup()  # This also stores



        log("Interval array stored for "+self.histoneMark)

    def calculateCoverages(self):
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


    def getRegions(self):
        return self.getRegionsFromLocalDB()



    def initializePropertiesStoreStructures(self,cgsAS, dataConnections):
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            # NJ dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT, neighborhood TEXT)")
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, neighborhood TEXT)")
        else:
            # no neighborhood
            # NJ dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT)")
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT)")



    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT, neighborhood TEXT (depending on useNeighborhood)

        # NJ This is likely now
        # regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, neighborhood TEXT (depending on useNeighborhood)

        regionData = []
        regionDataWithScores = []

        if result[2] > 0:
            # indicates that the regions overlaps with DNaseI hypersensitive site
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,self.histoneMark,str(result[5])])
            if result[1] >= 0.1:
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,self.histoneMark,str(result[5])])
            if result[1] >= 0.5:
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,self.histoneMark,str(result[5])])

            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,self.histoneMark,str(result[5]),wordFloat(result[1],2)])

        else:
            #the region does not overlap with a site, report distance to the nearest (not tissue specific)
            if str(result[5]) == "any":
                if result[4] < settings.MAX_DISTANCE:
                    dd  = wordMagnitude(result[4])
                    regionData.append([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,str(self.histoneMark),dd])
                if result[3] < settings.MAX_DISTANCE:
                    du  = wordMagnitude(result[3])
                    regionData.append([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,str(self.histoneMark),du])
                if result[4] < result[3]:
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.histoneMark),dd])
                elif result[3] < result[4]:
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.histoneMark),du])
                elif result[3] < settings.MAX_DISTANCE:
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.histoneMark),du])
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            index = 0
            # Neighborhood is demanded and computed for this dataset
            beforeStart =  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodBeforeStart")
            for i in xrange(len(beforeStart)):
                # NJ if result[8][i] == "1":
                if result[6][i] == "1":
                    regionData.append([settings.wordPrefixes["neighborhood"],
                                       self.datasetWordName,
                                       self.histoneMark,
                                       str(result[5]),
                                       "bs"+str(beforeStart[i])])
            bsl = len(beforeStart)
            afterEnd =  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodAfterEnd")
            for j in xrange(len(afterEnd)):
                # NJ if result[8][j+bsl] == "1":
                if result[6][j+bsl] == "1":

                    regionData.append([settings.wordPrefixes["neighborhood"],
                                   self.datasetWordName,
                                   self.histoneMark,
                                   str(result[5]),
                                   "ae"+str(afterEnd[j])])


        return regionData,regionDataWithScores


    def getWordPrefixes(self,cgsAS):
        wordPrefixes =  [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                ":".join([settings.wordPrefixes["overlapRatio"],self.datasetWordName,self.histoneMark]),
                ":".join([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,self.histoneMark]),
                ":".join([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,self.histoneMark]),
                ":".join([settings.wordPrefixes["minimumDistance"],self.datasetWordName,self.histoneMark])]
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            wordPrefixes.append(":".join([settings.wordPrefixes["neighborhood"],self.datasetWordName,self.histoneMark]))
        return wordPrefixes


    def getWordsDescription(self):
        # NJ ALSO WTF?

        doc = []
        for tissue in self.tissues:
            pass
        return doc

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
        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+":"+self.histoneMark+"::"+"Eor:"+self.datasetWordName+":"+self.histoneMark+":POS3SOP::2::0"])
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName+":"+self.histoneMark])
        featureWords.append(categoriesPath+["distanceTo"]+["Emdd:"+self.datasetWordName+":"+self.histoneMark+"::2::0"])
        featureWords.append(categoriesPath+["distanceTo"]+["Emud:"+self.datasetWordName+":"+self.histoneMark+"::2::0"])
        featureWords.append(categoriesPath+["distanceTo"]+["Emmd:"+self.datasetWordName+":"+self.histoneMark+"::2::0"])
        if annotationFeatures["useNeighborhood"]:
            bsN = ":".join(map(str,annotationFeatures["neighborhoodBeforeStart"]))
            aeN = ":".join(map(str,annotationFeatures["neighborhoodAfterEnd"]))
            featureWords.append(categoriesPath+["Enbh:"+self.datasetWordName+":"+self.histoneMark+"::"+bsN+"::"+aeN])
        return featureWords

    def getOverlappingText(self):
        return self.datasetWordName + ":" + self.histoneMark

    def getSubAnnotations(self):
        return self.tissues+["any"]
