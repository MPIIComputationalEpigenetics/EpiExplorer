import urllib2

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint


def processString(string):
    return string.replace('-', "").replace("_", "").replace("_","").replace("+", "").replace(".","").replace("(","").replace(")","").lower()

class EncodeHTMLParser(HTMLParser):
    def __init__(self):
        self.antibodies = {}
        self.actual = None
        self.links = None
        HTMLParser.__init__(self)
        self.is_in_table = False
        self.is_in_tr = False
        self.is_in_td = False
        self.is_in_a = False
        self.url = None
        self.link = None
        self.td_data = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.is_in_table = True

        if self.is_in_table and tag == "tr":
            self.is_in_tr = True
            self.actual = []

        if self.is_in_tr and tag == "td":
            self.is_in_td = True
            self.links = []
        
        if self.is_in_td and tag == "a":
            self.is_in_a = True
            self.url = attrs[1][1]
            if self.url[0] == "/":
                self.url = "http://genome.ucsc.edu" + self.url


    def handle_endtag(self, tag):
        if tag == "table":
            self.is_in_table = False

        if self.is_in_table and tag == "tr":
            self.is_in_tr = False
            if len(self.actual) > 0:
               self.antibodies[processString(self.actual[0])] = self.actual
            self.actual = []

        if self.is_in_tr and tag == "td":
            self.is_in_td = False
            if len(self.links) > 0:
                self.actual.append(self.links)
            else:
                self.actual.append(self.td_data)
            self.links = None
            self.data = None

        if self.is_in_a and tag == "a":
            self.is_in_a = False
            self.links.append( (self.link, self.url) )
            self.link = None
            self.url = None

    def handle_data(self, data):
        if self.is_in_td and not self.is_in_a:
            self.td_data = data.strip()

        elif self.is_in_a:
            self.link = data

class Vocabulary:
    def __init__(self):
        self.values = None

    def process_data(self, data):
        parser = EncodeHTMLParser()
        parser.feed(data)
        self.values = parser.antibodies
    
    def full(self, key):
        key = processString(key)
        if self.values.has_key(key):
            return self.values[key]
        return None

    def description(self, name):
        pass


class AntibodyVocabulary(Vocabulary):
    def __init__(self, fromURL = False):
        Vocabulary.__init__(self)
        if fromURL:
            f = urllib2.urlopen('http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&type=Antibody')
        else:
            f = file("../Datasets/Vocabulary/antibody.html")
        data = f.read()
        self.process_data(data)

    def description(self, antibody):
        antibody = processString(antibody)
        if self.values.has_key(antibody):
            return self.values[antibody][1]
        return None


class CellLineVocabulary(Vocabulary):
    def __init__(self, fromURL = False):
        Vocabulary.__init__(self)
        if fromURL:
            f = urllib2.urlopen('http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&type=Cell+Line')
        else:
            f = file("../Datasets/Vocabulary/cellline.html")
        data = f.read()
        self.process_data(data)

    def description(self, cellline):
        if self.values.has_key(cellline):
            return self.values[cellline][2]
        return None

#ac = AntibodyVocabulary()
#av = CellLineVocabulary()
#for s in ["GM12878", "H1hESC", "K562", "HelaS3", "HepG2", "HUVEC", "HMEC", "HSMM", "HSMMtube", "NHA", "NHDFAd", "NHEK", "NHLF", "Osteobl"]:
#    print s + " " + str (av.full(s))
#print (av.full("Pol2b"))
#print (ac.full("Pol2b"))

