from xml.etree.ElementTree import XMLParser
import urllib
from utilities import *
import settings

class ProcessCSQueryResult:                     # The target object of the parser
    
    def start(self, tag, attrib):   # Called for each opening tag.
        if tag == "result":
            #like an init
            self.query = ""
            self.totalCompletions = 0
            self.totalHits = 0
            self.completions = {}
            self.hits = {}
            self.isCompletion = False
            self.isHit = False
            self.isHitTitle = False
            self.isHitUrl = False
            self.isQuery = False            
        elif tag == "completions":
            self.totalCompletions = attrib["total"]
        elif tag == "hits":
            self.totalHits = attrib["total"]
        elif tag == "c":
            self.isCompletion = True
            self.currentComplNumber = attrib["dc"] 
        elif tag == "hit":
            self.isHit = True      
            self.currentHitData = {"title":"",
                                   "url":""}      
        elif tag == "query":
            self.isQuery = True
        else: 
            if self.isHit:
                if tag == "title":
                    self.isHitTitle = True
                elif tag == "url":
                    self.isHitUrl = True
                    
            
            
    def end(self, tag):             # Called for each closing tag.
        if tag == "c":
            self.isCompletion = False
        elif tag == "hit":
            self.isHit = False
            self.hits[self.currentHitData["title"]] = self.currentHitData["url"]
            self.currentHitData = None
        elif self.isHit:
            if tag == "title":
                self.isHitTitle = False
            elif tag == "url":
                self.isHitUrl = False
    def data(self, data):
        if self.isCompletion:
            self.completions[str(data)] = self.currentComplNumber
            self.currentComplNumber = None
        elif self.isHit:
            if self.isHitTitle:
                self.currentHitData["title"] = str(data)
            elif self.isHitUrl:
                self.currentHitData["url"] = str(data)
        elif self.isQuery:
            self.query = str(data)
            self.isQuery = False            
    def close(self):    # Called when all data has been parsed.
         return (self.query,self.totalCompletions,self.totalHits,self.completions,self.hits)
     
def getQueryResult(query,detailedLog=True):
    parser = XMLParser(target=ProcessCSQueryResult())
    queryAnswerXML = urllib.urlopen(query).read()
    if detailedLog:
        log_CSQuery(queryAnswerXML)
    parser.feed(queryAnswerXML)
    return parser.close()
