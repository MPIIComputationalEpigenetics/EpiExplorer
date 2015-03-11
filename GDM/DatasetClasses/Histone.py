# the regions are stored in a local file DB and the search structure is interval array
# This is a rehashing of BroadHistonesSingle.py with generic code extracted to BaseFeature.py

# import numpy  # maybe required if numpy type is redefined
import sqlite3
# import sys
import warnings

from utilities import *
import DatasetClasses.BaseFeature
import IntervalArray
import settings


class Histone(DatasetClasses.BaseFeature.BaseFeature):
    # Note 'init' not a constructor!! Will have to be called explicitly
    # todo rename init? This is really 'preprocess data'

    def __init__(self):
        DatasetClasses.BaseFeature.BaseFeature.__init__(self)
        # in 3.0 change this to super().__init__()
        self.define_annotation_values = self.define_distance_annotation_values
        self.define_insert_values = self.define_minimal_insert_values
        self.neighborhoodAfterEnd = '0,30,100,300,1000,3000,10000,30000,100000'
        self.neighborhoodBeforeStart = '100000,30000,10000,3000,1000,300,100,30,0'
        self.useNeighborhood = True  # Could drop this and simply test for above attrs

    def init(self, initCompute=True):  # Histone specific
        # Remove this when dependancy removed from CGSDataDatasetServer
        # and configs overhauled. FeatureType currently used in the noe generic computeSingleRegionProperties
        self.FeatureType = self.histoneMark
        DatasetClasses.BaseFeature.BaseFeature.init(self, initCompute)

    def calculateCoverages(self):
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()  # c is currently shadowing a global c?

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


    # This differs to Regions classes

    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT, neighborhood TEXT (depending on useNeighborhood)

        # NJ This is likely now
        # regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, neighborhood TEXT (depending on useNeighborhood)

        regionData = []
        regionDataWithScores = []

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


    # from the CGSTexts.js config is seems the tissue is added to the end of these strings somewhere?

    def getWordPrefixes(self,cgsAS):
        wordPrefixes =  [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                ":".join([settings.wordPrefixes["overlapRatio"],self.datasetWordName,self.FeatureType]),
                ":".join([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,self.FeatureType]),
                ":".join([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,self.FeatureType]),
                ":".join([settings.wordPrefixes["minimumDistance"],self.datasetWordName,self.FeatureType])]
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

        return settingsLocal

    def getOverlappingText(self):
        return self.datasetWordName + ":" + self.FeatureType

