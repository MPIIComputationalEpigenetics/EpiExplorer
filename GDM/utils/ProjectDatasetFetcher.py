#! /usr/bin/env python

# NOTE: This script assumes that the bigBedToBed binary (chmod +x!) is available in the environment $PATH. The
# init_epi_env.sh script automatically add the following default location to the $PATH:
#   $APP_BIN_DIR/kentUtils
# bigBedToBed is avaialable from kentUtils:
#   https://github.com/ENCODE-DCC/kentUtils
# or precompiled:
#   http://hgdownload.cse.ucsc.edu/admin/exe/
# wget -r -nH --cut-dirs=4 --no-parent -e robots=off --reject="index.html*"



# We probably want to enable reading files directly from the nfs mount point rather than copying
# them but that may require some deeper tinkering with the process data set code.
# As it currently expects it to be in teh standard hg19_DownloadedDataset locations and
# named to match the ini file or a derivative of the ini file if the original is a merged file

import optparse  # Can't use argparse as this was new in 2.7 sigh.
import sys, re, os.path, itertools

# EpixEplorer imports
# sys.path = [os.path.abspath(os.path.dirname(__file__) + "/..")] + sys.path
# Don't need to do this now as source root is added to PYTHONPATH in env/editor
import utilities

# /nfs/ftp/pub/databases/blueprint/releases/current_release/
# This is not the data root! Just the release root!
# This is the data root for blueprint: /nfs/ftp/pub/databases/


# These are the current header fields which will be stored in header_index
# EXPERIMENT_ID
# STUDY_ID
# STUDY_NAME
# CENTER_NAME
# FIRST_SUBMISSION_DATE
# SEQ_RUNS_COUNT
# SAMPLE_ID
# SAMPLE_NAME
# INSTRUMENT_PLATFORM
# INSTRUMENT_MODEL
# LIBRARY_NAME
# LIBRARY_LAYOUT
# LIBRARY_STRATEGY
# EXPERIMENT_TYPE
# READ_STRAND
# READ_QUALITIES
# MOLECULE
# SAMPLE_ONTOLOGY_URI
# DISEASE_ONTOLOGY_URI
# DISEASE
# BIOMATERIAL_PROVIDER
# BIOMATERIAL_TYPE
# CELL_LINE
# CELL_TYPE
# DONOR_ID
# DONOR_AGE
# DONOR_HEALTH_STATUS
# DONOR_SEX
# DONOR_ETHNICITY
# TISSUE_TYPE
# TISSUE_DEPOT
# POOL_ID
# POOLED_DONOR_IDS
# GENETIC_CHARACTERISTICS
# TREATMENT
# TWIN_PAIR_ID
# DONOR_REGION_OF_RESIDENCE
# SPECIMEN_PROCESSING
# SPECIMEN_STORAGE
# SAMPLE_SOURCE
# SAMPLE_BARCODE
# SAMPLE_DESCRIPTION
# FILE
# FILE_MD5
# FILE_SIZE
# FILE_TYPE
# NSC
# RSC
# EST_FRAG_LENGTH

# todo write file type descriptions for all of these and double check there is only 1 actual file/output type
# FILE_TYPEs
# BS_HYPER_METH_BB_CNAG
# BS_HYPER_METH_BED_CNAG
# BS_HYPO_METH_BB_CNAG
# BS_HYPO_METH_BED_CNAG
# CS_BROAD_MACS2
# CS_MACS2
# CS_MACS_TRACK_BB
# CS_MACS_TRACK_BROAD_BB
# DS_HOTSPOT
# DS_HOTSPOT_TRACK_BB

# The common strings here are HYPER_METH, HYPO_METH, MACS, MACS2 and HOTSPOT
# We need some long descriptions of these protocols and their outputs. Do these need to be sprintf'd to integrate the
# cell_type/line and feature type?

# mandatory_params = []
# Todo Change this to a base SourceDataFetcher class with simple project specific wrapper class which define config
# Then convert this script to dynamically import the correct class at runtime based on the project name
# This will remove ambiguity of some method names or necessity to have project specific names called using getattr
# and allow this to be imported by other code.
# Move options validation to base run method, so it can be used  more than once
# Would simply need to tranlsate parser options to arguments
# or can we get the options dict and pass a dictionary as a list to the main method
# This would allow removal of self import i.e. import __main__
# This will also break if attempts are made to import this as a package


# Todo handle fetching index file via ftp
# Todo handle converting regular ini file to default/query
# Todo Download/copy or just access files directly? Convert direct from source if local and bb
# Todo convert bb to bed? skip non bed/bb files? Seems like there is always a bb and a bed file. Should we bother to
# check for bb only? There are 416 bb files and only 310 bed files
# Note these are no ERR (reads IDs) as this is clinical/sensitive data. So there is no single reference which can be
# used to cache the info. It will be jointly on ERX, ERS

# todo if bb then we need to do datasetOriginal before we do the conversion
# todo write ftype grouped files!
# Do this here to allow print in options help
# This structure will not allow options specific access!
# rework so it is option centric and add an extra key for valid_projects, which is just used to validate
# but ignore when setting

verbose = False
assembly = 'hg19'

project_config = {
    'projects': ['blueprint'],  # Validation on this value, will also allow selective omission of other config
    'ftp_root': {'blueprint': 'http://ftp.ebi.ac.uk/pub/databases/'},

    # This is used to define the python class and also used in identify_class which used
    # in the datasetWordName (i.e. the index), so keep these small
    # Could do with something more specific/smaller for use with the datasetWordName
    # e.g. BS-Seq(RRBS/RRBS), Hist, DNase. Currently this is hardcoded in the assign methods
    'exp_classes': {'blueprint': {'DNase-Hypersensitivity': 'DatasetRegionsWithTissues',
                                  'Bisulfite-Seq': 'DNAMethylation',
                                  'H3K9or14ac': 'Histone'}},
    'valid_strats': {'blueprint': {'bs': 'Bisulfite-Seq',
                                   'cs': 'ChIP-Seq',
                                   'ds': 'DNase-Hypersensitivity'}},
    # These classes should ultimately support different output types and multiple tissues
    # and feature types i.e. is TFBS similar enough to Histone to share the class?
    # DNase may have substantially different qualities depending on the tech
    # Is RR and WG BS-Seq similar enough to handle with the same class
    # The feature_types should be either handled in class by control flow or delegation
    # with the high level classes handling the tech?
    # some of these would never delegate
    # exception here seems to be DNase which is already very feature type specific
    # leaving the tech to be variable
    # leaving the tech to be variable
}


def set_project_config_attrs(project):
    global project_config
    # project validation currently done by choice option

    for var, value in project_config.iteritems():
        if var == 'projects':
            continue

        setattr(__main__, var, value[project])


    # strat_code is only used to prevent having to use full length strat names in assign function names
    # which are not PEP8 compliant and may break things

    # This is blueprint specific?

    # Invert valid_strats
    if hasattr(__main__, 'valid_strats'):
        # strat_codes = {v: k for k, v in valid_strats.iteritems()} # no dictionary comprehension until 2.7 drat!
        __main__.strat_codes = dict((v,k) for k, v in __main__.valid_strats.iteritems())

    return


def parse_blueprint_index(index_file, filter_vars):
    global verbose
    index_fh = open(index_file, "r")

    # READ HEADER #
    # Index will protect against file format changes and will also facilitate filter_vars match
    header_index = {}
    i = 0

    for var in index_fh.readline().strip().split():
        header_index[var] = i
        i += 1

    # READ REST OF FILE #
    exp_cache = {}

    for line in index_fh:
        line = line.strip().split("\t")
        break_out = False

        # Handle known cases, most common first for speed
        file_matches = re.match(r"(.*)\.(bb|bed)(\.gz)?$", line[header_index['FILE']])

        if not file_matches:

            if verbose:
               print ("Skipping non-bed format file:\t" + line[header_index['FILE']] + "\t" +
                   line[header_index['FILE_TYPE']])

            continue

        file_prefix = file_matches.group(1)
        file_suffix = file_matches.group(2)

        # Is this hardcoded to skip dnase and what else?

        if (re.match('DS_HOTSPOT', line[header_index['FILE_TYPE']]) and
            re.match('.*_peaks\.', line[header_index['FILE']])):
            continue

        # print line[header_index['FILE_TYPE']] + ' ' + line[header_index['FILE']]

        for var_name, var_values in filter_vars.iteritems():
            # print "var_name/values\t" + var_name + ":" + str(var_values)

            if line[header_index[var_name]] in var_values:

                if verbose:
                    print "Identifed:\t" + line[header_index['FILE_TYPE']] + ' ' + line[header_index['FILE']]

                # Build exp_cache here to resolve FILE_TYPE redundancies
                # Bed format is preferential to bigBed, but conversion can be done later if required
                # Currently there can be .bed.gz and .bb files for the same data.
                # These will have FILE_TYPEs as follows:
                #     *.bed.gz: ANALYSIS_TYPE
                #     *.bb:     ANALYSIS_TYPE_BB
                # The standard FILE_TYPE will does have the bed format encoded in the string, so it is also necessary to
                # validate the FILE name field. In addition, there are some FILEs which are erroneously given the same
                # FILE_TYPE e.g.
                #     ERX197157 C004084E.DNase.hotspot_v3.20130415.bed.gz       DS_HOTSPOT
                #     ERX197157 C004084E.DNase.hotspot_v3_peaks.20130415.bed.gz DS_HOTSPOT
                # In these cases the peaks file is currently being ignored

                # Identify if FILE_TYPE is sub-string or super-string of current keys
                # This approach is flawed as we may have other valid sub-strings for analysis with different outputs.
                # Therefore, need to be specific about BB suffix. But there is no guarantee it will be a suffix:
                #   BS_HYPER_METH_BB_CNAG
                #   BS_HYPO_METH_BB_CNAG
                #
                # Will have to rely on path-prefixes instead
                exp_id = line[header_index['EXPERIMENT_ID']]

                # No way of testing for redundant bed files, but there shouldn't be
                # only redundancies between bed and bb

                # Defined dict value to avoid KeyError below
                prefix_paths = exp_cache.setdefault(exp_id, {})

                # Preferentially take .bed over .bb
                # has_key removed in python 3
                if (file_suffix == "bed") or file_prefix not in prefix_paths:
                    exp_cache[exp_id][file_prefix] = line
                    break_out = True
                    break

            # end of if line[header_index[var_name]] in var_values:

            if break_out:
                break
                # end of for var_name, var_values in filter_vars:

    # end of for line in index_file:

    return exp_cache, [header_index]

# These need to be in __main__ for getattr to work
# It would be nice to have them in the process_blueprint_dataset function defined at compile time rather than runtime
# Would not affect performance, would just serve to as useful encapsulation,can we do somethign like:
#   getattr(__main__.process_blueprint_dataset, 'function')
# Correct solution is to turn this into a base and project specific wrapper class

def assign_ds_info(ini_dict, line, header_idx):
    ini_dict['features'] = 'overlapBinary, overlapRatio, distanceToNearest'
    ini_dict['dataCategories'] = [ ini_dict['genome'] + 'DNase1' ]  # This was actually null
    ini_dict['hasFeatures'] = True
    ini_dict['hasGenomicRegions'] = True
    # reset some default values

    ini_dict['datasetOfficialName'] = 'DNase1'  # Would otherwise be 'Chromatin Accessibility'

    # default value is  hg19_Blueprint_Chromatin Accessibility
    ini_dict['datasetSimpleName'] = ini_dict['genome'] + "_Blueprint_DNase1"
    # ini_dict['filterByColumn'] = -1

    # May need to extend datasetWordName to differentiate between data types
    # which share the same data_class
    ini_dict['datasetWordName'] = 'bp_DNase1'

    # These should be defaults in the class itself, assuming bed format input
    # Then we could just specify bed, or even implicitly validate the format?
    ini_dict['chromIndex'] = 0
    ini_dict['chromStartIndex'] = 1
    ini_dict['chromEndIndex'] = 2
    return


def assign_cs_info(ini_dict, line, header_idx):
    # Normally this
    # features = overlapBinary, overlapRatio, distanceToNearest
    # But for
    # hg19_Broad_Histones_H2AZ.ini:features = overlapBinary, overlapRatio, distanceToNearest ,neighborhood
    # hg19_Broad_Histones_H3K79me2.ini:features = overlapBinary, overlapRatio, distanceToNearest ,neighborhood
    # we have this?
    # features = overlapBinary, overlapRatio, distanceToNearest ,neighborhood
    # From encode:
    # H2A.Z	Peak	Histone protein variant (H2A.Z) associated with regulatory elements with dynamic chromatin
    # H3K79me2	Region	Transcription-associated mark, with preference for 5 prime end of genes
    # So nothing outstanding
    # Either this is no longer used or it is used because of the length of these features or the nature of their
    # neighbourhood

    ini_dict['dataCategories'] = [ ini_dict['genome'] + 'histones' ]
    ini_dict['histoneMark'] = line[header_idx['EXPERIMENT_TYPE']]

    # Not sure this is even used anymore?
    ini_dict['features'] = 'overlapBinary, overlapRatio, distanceToNearest'

    # These defaults are now in Histone.__init__
    # ini_dict['neighborhoodAfterEnd'] = '0,30,100,300,1000,3000,10000,30000,100000'
    # ini_dict['neighborhoodBeforeStart'] = '100000,30000,10000,3000,1000,300,100,30,0'
    # ini_dict['useNeighborhood'] = True  # If this is related to above vars why is this even needed?

    # These are not present in the standard bed format and appear not to be referenced anywhere else in the code base
    # #Although may be used in plicitly in otherScoreIndeces in readDatasetFromFileObject?
    # pValueIndex = 8
    # signalValueIndex = 7
    # We do have a score field, but unsure what this is and may change between FILE_TYPE



    #todo redefine default description with something more wordy
    #ini_dict['datasetDescription'] = "This track displays maps of chromatin state generated by the Broad/MGH ENCODE group using ChIP-seq. Chemical modifications (methylation, acylation) to the histone proteins present in chromatin influence gene expression by changing how accessible the chromatin is to transcription. ### ### The ChIP-seq method involves cross-linking histones and other DNA associated proteins to genomic DNA within cells using formaldehyde. The cross-linked chromatin is subsequently extracted, mechanically sheared, and immunoprecipitated using specific antibodies. After reversal of cross-links, the immunoprecipitated DNA is sequenced and mapped to the human reference genome. The relative enrichment of each antibody-target (epitope) across the genome is inferred from the density of mapped fragments."
    #utilities.warning("assign_cs_info harcoded for histone info")
    return


# DatasetClass code does not yet handle dual hyper/po input files or multiple tissues
# convert to individual inis using:
#

def assign_bs_info(ini_dict, line, header_idx):
    ini_dict['dataCategories'] = [ ini_dict['genome'] + 'methylation' ]
    # Not sure this is even used anymore?
    ini_dict['features'] = 'percentCpGwithData,numberOfCpGwithData,averageRatio,stdRatio,minRatio,maxRatio'
    ini_dict['datasetOfficialName'] = 'BisSeq'  # Change to 5mC?
    # probably need to add in assay/analysis type in here, for generic DNAMethylation class to handle?
    # These are expected to be processed features, so we don't need to worry about potential different
    # raw data formats from different technologies
    # default value is  hg19_Blueprint_Chromatin Accessibility
    ini_dict['datasetSimpleName'] = ini_dict['genome'] + "_Blueprint_BisSeq"
    # default is bp_OpenChromatin
    ini_dict['datasetWordName'] = "bp_BisSeq"
    # May need to extend datasetWordName to differentiate between data types
    # which share the same data_class
    # ini_dict['datasetWordName'] += '???'

    return


def process_blueprint_datasets(ini_dir, exp_cache, project_vars):
    global assembly
    header_index = project_vars[0]
    exp_classes = __main__.exp_classes
    #valid_strats = __main__.valid_strats
    strat_codes = __main__.strat_codes
    ftp_root = __main__.ftp_root
    # compile substitution regexs outside loop for speed
    cell_regex = re.compile(",?( )+")
    exp_type_regex = re.compile("/")
    file_info = []

    # don't really need this loop in here (will create redundancy between process_project_dataset)
    # But will protect against data model issues e.g. if one dataset is defined by 2 files?
    # Will also simplify config by allowing some vars set up outside of loop just once.


    # Now we need to group experiments by ftype, and add to tissues/datasetFrom
    # This currently assumes there are no redundancies across the file_prefixes for ftype
    dset_cache = {}

    for exp_id, file_type_cache in exp_cache.iteritems():
        # do we really need hg19 pre-fix? Doesn't genome var take multiple values?
        # Just do as before for now
        # Can we just use 'Blueprint' instead of CENTER_NAME? Depends on clashes?
        # The strat should be implicit from the ftype so leave that out?
        # CELL_TYPE or CELL_LINE? Depend on clashes
        # CELL_TYPE can have spaces and can be long
        # Each line will have 1 or other, but never none or both.
        # Can we cache these and make multi tissue inis?
        # Would likely need to translate comma's and spaces. Depending on how tissues is parsed
        # multi-tissue inis seem to have just one datasetFrom file, a merge which has been dumped from a DB.
        # Just write individual inis for now. As datasetFrom usage is peppered all over the place
        # This could be refactored to take a tissue argument and return the relevant file
        # based on synced datasetFrom & tissues lists

        # Change comma to ;? How will code handle spaces in tissue strings?

        # Cache key is EXPERIMENT_ID, FILE_TYPE?
        # No FILE_TYPE will change between formats!
        # Compressed format type will be appended to uncompressed file type which may not have the file format in it!
        # Just check the file names!
        # This will identify redundancies between file formats
        # We should preferentially take bed, and if absent convert from bb
        # Need to cache all first to make this decision

        # Need to investigate download code to insert bb to bed conversion

        # Need to discriminate between output type!
        # Can we just check for sub string?
        # Preferentially taking the shorter file type, and deleting/ignoring the longer version
        # Need to allow more than one file per experiment, as some analyses have more than one output

        # How are we going to encode the file types in the names?
        # Will this be the word name?

        for file_prefix, line in file_type_cache.iteritems():
            # Handle single H3K9/14ac, convert / to or
            # This is really only a problem with the path? Can we keep this for the variables?
            # This will likely be used in another file name somewhere
            exp_type = exp_type_regex.sub('or', line[header_index['EXPERIMENT_TYPE']])

            # Handle commas & spaces
            # CD14-positive, CD16-negative classical monocyte
            # CD34-negative, CD41-positive, CD42-positive megakaryocyte cell
            # CD4-positive, alpha-beta T cell
            # CD8-positive, alpha-beta T cell
            #cell = cell.replace(',', '+')

            if (line[header_index['CELL_TYPE']] != "-"):
                cell = line[header_index['CELL_TYPE']]
            elif (line[header_index['CELL_LINE']] != "-"):
                cell = line[header_index['CELL_LINE']]
            else:
                cell = line[header_index['TISSUE_TYPE']]

            cell = cell_regex.sub('_', cell)

            # The following names omit the cell for multo-tissue inis
            # display_label = '_'.join([cell, exp_type])
            simple_name = '_'.join([assembly, 'Blueprint', exp_type])

            if simple_name not in dset_cache.iterkeys():
                exp_class = identify_class(line[header_index['LIBRARY_STRATEGY']], exp_type)

                ini_info = {'datasetSimpleName': simple_name,   # 'group' name for all cell type data for this feature type
                            # redefine either of these in the assign methods as required
                            # Probably want to reduce the size of datasetWordName as it is used in the indexes
                            # We need to ensure words are non-redundant between projects
                            # ALso data_class may cause problems if a data_class can process > 1 data type
                            # e.g. DNAMethylation: RRBS and WGBS or OpenChromatin: DNase1, FAIRE etc.
                            # So we need something a bit more specific than the exp_class

                            'datasetWordName': "bp_" + exp_class,

                            'datasetOfficialName': exp_type,  # display_label,
                            # This is highly dependant on data type
                            # is 'Chromatin Accessibility' for DNase-Hypersensitivity
                            # Set this in the assign methods?

                            # dataCategories:      Mandatory - Slash(/) separated list of data categoires.
                            # Used in index, so order appears to matter and should match other data sets with
                            # same categories. ??!! This may cause issues. Really need to validate, sort or
                            # standardise in some way.
                            # Data structure here is also potentially restrictive. These are currently valid:
                            #   Tiling/ Genome-wide
                            #   Tiling/ Around genes
                            # But what about:
                            #   Tiling/ Genome-wide / category_x
                            #   Tiling/ Around genes / category_x
                            # This will not allow querying based on Tiling /category_x
                            # Also, why was this never prefixed with the assembly?
                            # This is quite often prefixed with the assembly too, but these are likely
                            # not strictly needed as there will never be mized assembly data in the same index
                            # So it's likely just a file naming issue.
                            # It looks like this list data structure may have been abandoned,
                            # but persists as legacy config/code
                            # It's also unclear to me the relationship between this and the datasetWordName
                            # Both appear to be used in the index, but only the categories appear to require
                            # the assembly differentiation

                            'genome': assembly,
                            'tissues': [],  # cell,
                            # 'hasBinning': False,  # True only for query sets, and optional
                            'hasGenomicRegions': False,
                            'regionsFiltering': 'combineOverlaps',
                            # Always combineOverlaps apart from gene like inis which also have: remove duplicates, merge gene names

                            # default bed indexes
                            # These should probably be set dynamically based on file type
                            # These are now the defaults
                            #'chromIndex': 0,
                            #'chromStartIndex': 1,
                            #'chromEndIndex': 2,
                            'datasetPythonClass': exp_class + '.py',
                            #This path is relative to ini file?
                            #This now supports paths relative to DatasetClasses
                            #This should really be optional and default to FeatureClass.py


                            'datasetFrom': [],# ftp_root + line[header_index['FILE']],
                            # 'datasetOriginal': ftp_root + line[header_index['FILE']],
                            # This was only used in the hg18/9_PutativeenhancersErnstetal.ini files
                            # It is still used in restartUserDatasetComputation, so probably only required for
                            # user data sets, as that's how the Enhancers were originally loaded?
                            # This is likely only used by code very specific to that class, and is probably not required?

                            'datasetDescription': build_description(line[header_index['FILE_TYPE']], cell, exp_type),  # description.replace("###","\n"), #todo
                            'datasetMoreInfo': [],#exp_id,  # todo expand to full ENA url?
                            # This seems to be a url prefix for multi-tissue inis
                            # e.g. http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid

                            #'datasetType': "Default",  # seemingly only ever set to II27 for Illumina Infinium sets

                            # CGSDatasetServer.datasetInfo only
                            # 'numberOfRegions': 0,
                            # 'isDefault': False,
                            # 'overlappingText': datasetName
                }

                # These are the remaining Histone vars, but we probably need to tweak these for single datasets versus
                # multiple datasets across tissues
                # dataCategories
                # datasetDescription


                # ini_info['additionalSettingsFile'] = str(additionalSettingsFileName)

                # This should update ini_info object
                #assign_strat_info[line[header_index['LIBRARY_STRATEGY']]](ini_info, line, header_index)
                assign_strat_ref = getattr(__main__,
                                           "assign_" + strat_codes[line[header_index['LIBRARY_STRATEGY']]] + "_info")
                assign_strat_ref(ini_info, line, header_index)
                dset_cache[simple_name] = ini_info

            # end of if simple_name not in dset_cache.iterkeys():

            # Add the tissue/file
            # These are reserved characters  ":", ",", "#", ";", "&", "*"
            # Need to validate these in readDatasetDescriptions.py or better still Dataset.py
            # tissues values will be used in word prefixes, but also in web display, so we really want to keep these
            # short. Ideally want some display lavel or acronym, but many a long wordy names
            # sample name is also required for differentiation or redundant samples on the same tissue.

            # Also need to avoid - in datasetSimpleName, as this is used the sqlite2 table name
            # Also need to avoid () datasetSimpleName and tissues as this can do odd things with file names
            # specifically when calling bedtools sort, but only in some circumstances, currently not error caught either

            dset_cache[simple_name]['tissues'].append((cell + "-" + line[header_index['SAMPLE_NAME']]))
            dset_cache[simple_name]['datasetFrom'].append(ftp_root + line[header_index['FILE']])
            dset_cache[simple_name]['datasetMoreInfo'].append(exp_id)


        # end of for file_type, line in file_type_cache.iteritems():
    # end of for exp_id, file_type_cache in exp_cache.iteritems():


    # Move this to main?

    for simple_name, ini_info in dset_cache.iteritems():
        out_file = ini_dir + simple_name.replace(' ', '_') + ".ini"
        print "Writing ini file:\t" + out_file
        utilities.write_dataset_ini_file(out_file, ini_info)
        utilities.write_dataset_ini_file(out_file, ini_info)



    # Log/count here for summary output?
    # Count some default fields and/or those which were filtered?



    # actually no TFBS for Blueprint, but leave this here for now, until we decide to remove validate_histone_string
    tfbs_report = ''

    for tfbs, exp_class in exp_classes.iteritems():

        if exp_class == 'TFBS':
            tfbs_report += "\t" + tfbs + "\n"

    if tfbs_report:
        print ("This script does not yet explicitly support TFBS as they are not currently a part of Blueprint.\n" +
               "Please manually inspect the automatic TFBS classifications are correct:\n" + tfbs_report + "\n" +
               "If these are valid this script needs updating to fully support TFBS")
        # todo validate_histone_string may not be working properly so print histone matches,
        # just to make sure we haven't mismatched?

    # TODO Write summary output here

    return file_info


def build_description(file_type, cell_name, exp_type):
    """ Default description method """
    utilities.warning("build_description returning empty test string")
    return ""


def identify_class(lib_strat, exp_type):
    exp_classes = __main__.exp_classes
    global brno_regex
    exp_class = ''

    if lib_strat in exp_classes:
        exp_class = exp_classes[lib_strat]
    elif exp_type in exp_classes:
        exp_class = exp_classes[exp_type]
    elif utilities.validate_histone_string(exp_type):  # Assign Histone by regex
        exp_class = exp_classes[exp_type] = 'Histone'
    else:  # Must be TFBS ?
        # Actually no TFBS for Blueprint, but let's leave it here for now
        exp_class = exp_classes[exp_type] = 'TFBS'

    return exp_class

'''

def downloadFileFromFTP(urlBed,localBed, force=False):

    if not force:
        if os.path.isfile(localBed):
            print time.strftime("%d.%m %H:%M:%S"),"File",localBed,"already exists"
            return

    print time.strftime("%d.%m %H:%M:%S"),"Downloading",urlBed
    #main method via urllib
    #downloadFile(urlBed,localBed)
    # Alternative version
    # wget
    wgetCommand = 'wget -nv -O "'+localBed+'" "'+urlBed+'"'
    os.system(wgetCommand)
    #print time.strftime("%d.%m %H:%M:%S"),wgetCommand
    print time.strftime("%d.%m %H:%M:%S"),"Downloaded",urlBed


def extractFileFromGzBed(localGzBed,outputFile):
    if os.path.isfile(outputFile):
        print time.strftime("%d.%m %H:%M:%S"),"File",outputFile,"already exists"
        return
    print time.strftime("%d.%m %H:%M:%S"),"Extracting",localGzBed
    f = gzip.open(localGzBed, 'rb')
    file_content = f.read()
    f.close()
    fw = open(outputFile,"w")
    fw.write(file_content)
    fw.close()
    print time.strftime("%d.%m %H:%M:%S"),"Extracted",localGzBed


def sortBed(bedFile,bedFileSorted):
    if os.path.isfile(bedFileSorted):
        print time.strftime("%d.%m %H:%M:%S"),"File",bedFileSorted,"already exists"
        return
    print time.strftime("%d.%m %H:%M:%S"),"Sorting",bedFile
    os.system(rsegBaseFolder+"bin/sortbed "+bedFile +" -o "+bedFileSorted)
    print time.strftime("%d.%m %H:%M:%S"),"Sorted",bedFile

'''


# To truly make this generic, the format filtering needs to be generic
# currently tied to blueprint header fields. Best options would be to move all generic code to a base class
# then write format/project specific wrappers.
# Alternative would be to delegate to project/format specific parsers, but we would still have an issue with
# the option processing.

def main():
    global project_config, verbose, assembly
    #assembly = 'hg19'  # todo This could be used as a filter, also implement as option?
    default_strat = 'ChIP-Seq'  # blueprint specific, remove or move to (process_)project_config
    default_project = 'blueprint'

    parser = optparse.OptionParser(usage="usage: %prog [options] /path/to/blueprint_dated.data.index",
                                   version="%prog 1.0")
    # NOTE: \n and 't meta characters in help strings below are ignored by optparse, prefixing string with r(aw)
    # simply prints the meta character and does not interpolate
    parser.add_option('-C', '--center_name', action='append', dest="centers", type="string", default=[],
                      help="Specifies CENTRE_NAME(s) to process")
    parser.add_option('-c', '--cell_type',  # action='store', # optional because action defaults to "store"
                      dest='ctypes', type='string', default=[], help="Specifies CELL_TYPE(s) to process")
    parser.add_option('-l', '--cell_line', dest='clines', type='string', default=[],
                      help="Specifies CELL_TYPE(s) to process")
    # make this additive rather then exclusive wrt cell_type
    # how are we going to handle multiple EXPERIMENT_TYPEs which cross LIBRARY_STRATEGIES?
    # simply don't, make them strats and ftypes exclusive
    # this assumes there won't ever be redundancy of ftypes between strats
    # Can't have choices dependant on project unless, as they have not been defined yet
    # Just restrict to blueprint for now.


    parser.add_option('-s', '--strat', type='choice',
                      #choices=[proj_dict.keys for proj_dict in project_config['valid_strats'].values()],
                      choices=list(itertools.chain.from_iterable([proj_dict.keys() for proj_dict in project_config['valid_strats'].values()])),
                      # strat_names, #change this to a dict comprehension to list all valid strats across projects
                      action='append', dest='strats', default=[],  # True default wont appear in man
                      # default=list(valid_strats.iterkeys()),  # This would append to the defaults, not over-write
                      # enable the full strat names as valid too?
                      help=("Restricts to specified LIBRARY_STRATEGY(s). Default = " + default_strat +
                            ".Valid values are:\n" + str(project_config['valid_strats'])))
    parser.add_option('-f', '--feature_type', type='string', action='append', dest='ftypes', default=[],
                      help="Specifies EXPERIMENT_TYPE(s) to process. e.g. H3K4me3 etc.")
    parser.add_option('-i', '--ini_dir', type='string', help="Mandatory: Specifies output ini_dir")
    parser.add_option('-d', '--data_dir', type='string', help="Mandatory: Specifies output data_dir")
    parser.add_option('-L', '--local_root', type='string', help="Copies data from --local_root to --data_dir")
    parser.add_option('-p', '--project', type='choice', choices=project_config['projects'],
                      default='blueprint', help="Project name e.g." + default_project)
    parser.add_option('-D', '--download', action='store_true', default=False,
                      help=("Downloads data to --data_dir from default ftp_root for your project:\t" +
                            str(project_config['ftp_root'])))
    parser.add_option('-v', '--verbose', action='store_true', default=False, help="Verbose output")
    ### PROCESS OPTIONS ###
    # Other options
    # -a --assembly global hardcoded to ahg19 at present
    # -f --ftp_root (this would be a config over-ride)
    # -A --All process all? This is accounted for by default strats
    (options, args) = parser.parse_args()
    # Doesn't need trying, as invalid project should have been detected by choice options
    project = options.project
    verbose = options.verbose

    set_project_config_attrs(project)
    # Can now access all project config via __main__


    if len(args) != 1:
        parser.error("Expects a single index file/path argument")

    index_path = args[0]

    # todo Need validate cell_type/line and add to filter_vars
    # Logic is inclusive not exclusive, currently handling this by making strats and ftype exclusive but what
    # about ctypes? Would need to count matches for each row and make sure they match the number of filter_vars keys
    filter_vars = {}

    # Validate options
    if options.ftypes:

        if options.strats:
            parser.error("-s/--strat and -f/--feature_type options are mutually exclusive")

        filter_vars['EXPERIMENT_TYPE'] = options.ftypes

    if not options.ftypes and not options.strats:
        options.strats = [default_strat]
            #__main__.valid_strats.values()
        # options.strats = valid_strats.copy()
        # del options.strats['rs']  # We don't want RNA-Seq as a default set
        # options.strats = options.strats.values()


    if options.strats:
        # TODO Still need to validate this strat is valid for the given project
        # The choices validation above uses strats from all projects
        filter_vars['LIBRARY_STRATEGY'] = []

        for strat_code in options.strats:
            if strat_code not in __main__.valid_strats:
                parser.error("-s/--strat " + strat_code + " is not valid for project " + project)

            filter_vars['LIBRARY_STRATEGY'].append(__main__.valid_strats[strat_code])


    if options.local_root and options.download:
        parser.error("The --local_root (copy) and (ftp) --download options are mutually exclusive. Please choose one.")

    if not options.ini_dir:
        parser.error("Mandatory option not specified:\t --ini_dir | -i")

    options.ini_dir = os.path.join(options.ini_dir, '')  # Add trailing slash if absent

    if not os.path.isdir(options.ini_dir):
        sys.exit("The -i(ni_dir) specified is not a directory or does not exist:\t" + options.ini_dir)

    ### PARSE PROJECT INDEX ### e.g. parse_blueprint_index
    exp_cache, project_vars = getattr(__main__, "parse_" + project + "_index")(index_path, filter_vars)

    ### BUILD DATASET_INFO AND WRITE INI ### e.g process_blueprint_experiments
    file_info = getattr(__main__, "process_" + project + "_datasets")(options.ini_dir, exp_cache, project_vars)

    # We can process bb to bed directly
    # Should probably try and thread this
    # Need to make processing use same code? This will currently only ever be bigBedToBed
    #

    # Just do this manually for now.

    # Or directly through b
    #grep -h datasetFrom *ini | sed 's/,/ /g' | sed 's/datasetFrom = //' | while read l; do for f in $l; do o=$(echo $f | sed 's&http://ftp.ebi.ac.uk/pub&&'); bigBedToBed /nfs/ftp/pub/$o $(echo $f | sed -r 's/.*\/(.*)(.bb$)/\1.bed/'); done; done


    #This also needs to be sorted an gzipped

    '''
    if options.local_root:
        sync_or_process_files(file_info)
    elif options.download:
        download_and_process_files(file_info)
    '''

    # TODO check createRoadmapDatasetInfo for anything else that might have been missed?
    # TODO add in download option, need to do that before writing ini? Only if file conversion is required
    # as would need to specify datasetOriginal? Is this absolutely required. Can't we just silently do the conversion?
    # What about skipping download if file is present. copy to .tmp, then rename trick, or do MD5
    # Need to support ftp and simple cp/rsync. rsync -a will pick up unfinished downloads!
    # Need to specify a source_root

    # todo write section for main unix_hg19.ini

    ### DOWNLOAD/REFORMAT SOURCE DATA ###


# end of main

if __name__ == '__main__':
    import __main__
    main()

"""
We need to get the unique values for all the required fields for each type, to see what is appropriate
For instance, it seems the STUDY_NAME is not appropropriate for DNAse dataset names as it does not contain the cell type. Done we want the sample name in there too?

    EXPERIMENT_ID   STUDY_ID        STUDY_NAME      CENTER_NAME     FIRST_SUBMISSION_DATE   SEQ_RUNS_COUNT  SAMPLE_ID       SAMPLE_NAME     INSTRUMENT_PLATFORM     INSTRUMENT_MODEL        LIBRARY_NAME    LIBRARY_LAYOUT  LIBRARY_STRATEGY   EXPERIMENT_TYPE  READ_STRAND     READ_QUALITIES  MOLECULE        SAMPLE_ONTOLOGY_URI     DISEASE_ONTOLOGY_URI    DISEASE BIOMATERIAL_PROVIDER    BIOMATERIAL_TYPE        CELL_LINE       CELL_TYPE       DONOR_ID        DONOR_AGE       DONOR_HEALTH_STATUS DONOR_SEX       DONOR_ETHNICITY TISSUE_TYPE     TISSUE_DEPOT    POOL_ID POOLED_DONOR_IDS        GENETIC_CHARACTERISTICS TREATMENT       TWIN_PAIR_ID    DONOR_REGION_OF_RESIDENCE       SPECIMEN_PROCESSING     SPECIMEN_STORAGE    SAMPLE_SOURCE   SAMPLE_BARCODE  SAMPLE_DESCRIPTION      FILE    FILE_MD5        FILE_SIZE       FILE_TYPE       NSC     RSC     EST_FRAG_LENGTH

    ERX406945       ERP001663       ChIP-seq data for cells in the haematopoietic lineages, from adult and cord blood samples.      NCMLS   19-MAR-2014 09:42:15    1       ERS358691       S00BS4H1        ILLUMINA        Illumina HiSeq 2000Blueprint_S00BS4H1_H3K4me3       SINGLE  ChIP-Seq        H3K4me3 -       phred   genomic DNA     http://purl.obolibrary.org/obo/CL_0000890;http://purl.obolibrary.org/obo/UBERON_0013756 NA      None    NIHR Cambridge BioResource      Primary Cell Culture        -       alternatively activated macrophage      S00BS4  -       NA      Female  NA      Venous blood    -       -       -       -       -       -       East Anglia     fresh   NA      Venous blood    S00BS4  alternatively activated macrophage  blueprint/data/homo_sapiens/Venous_blood/S00BS4/alternatively_activated_macrophage/ChIP-Seq/NCMLS/S00BS4H1.H3K4me3.ppqt_macs2_v2.20140513.xls.gz        94324ff67dd2858dd9d81a246187c5ed        746805  CS_MACS2    1.105296        3.889757        175,295,325

    ERX197157       ERP001748       DNase accessibility     NCMLS   21-JAN-2013 08:59:06    1       ERS206426       C004084E        ILLUMINA        Illumina HiSeq 2000     Monocytes_DNaseI_60U_C004084E_13M_startingcells SINGLE  DNase-Hypersensitivity      Chromatin Accessibility -       phred   genomic DNA     http://purl.obolibrary.org/obo/CL_0002057;http://purl.obolibrary.org/obo/UBERON_0013756 NA      None    NIHR Cambridge BioResource      Primary Cell    -       CD14-positive, CD16-negative classical monocyte     C00408  55 - 60 NA      Male    Northern European       Venous blood    -       -       -       -       -       -       East Anglia     fresh   NA      Venous blood    C00408  CD14-positive, CD16-negative classical monocyte     blueprint/data/homo_sapiens/Venous_blood/C00408/CD14-positive_CD16-negative_classical_monocyte/DNase-Hypersensitivity/NCMLS/C004084E.DNase.hotspot_v3_peaks.20130415.bed.gz     410bc4b1495127eaf075a75b8eee9369    1240520 DS_HOTSPOT      1.188587        0.9845632       60

    ERX301129       ERP002159       Bisulfite-Seq   CNAG    16-AUG-2013 10:50:09    8       ERS337609       G204    ILLUMINA        Illumina HiSeq 2000     594F_BS SINGLE  Bisulfite-Seq   DNA Methylation -       -       genomic DNA     http://purl.obolibrary.org/obo/CL_0000786   http://ncimeta.nci.nih.gov/ncimbrowser/ConceptReport.jsp?dictionary=NCI%20MetaThesaurus&code=C0026764   Multiple myeloma        Felipe Prosper,University of Navarra in collaboration with Jose I. Martin-Subero,  Institut d'Investigacions Biomediques August Pi i Sunyer Primary Cell    -       Plasma cell     25145   50 - 55 Multiple myeloma        Male    NA      Bone marrow     -       -       -       -       -       -       -  -
            -       Bone marrow     25145   Multiple myeloma        blueprint/data/homo_sapiens/Bone_marrow/25145/Multiple_myeloma/Bisulfite-Seq/CNAG/G204.CPG_methylation_calls.bs_call.20140106.bw        0ad087270396466e96dab441446513a7   69577388 BS_METH_CALL_CNAG       -       -       -

There are some cases where CELL_LINE and CELL_TYPE are not populated, in this case



    """


