import time
import datetime
import utilities
import settings

class ReportManager:
    def __init__(self, datasetServer):
        self.datasetServer = datasetServer
        self.initStats()   
        self.logTimeFormat = "%d.%m %H:%M:%S"
        
    def initStats(self):
        self.currentTime = time.time() 
        self.reportStats = {"Errors":[],
                            "DatasetsSubmited":[],
                            "DatasetsComputed":[],
                            "DatasetsWaiting":[],
                            "DatasetsQueue":None,
                            "AnalysisCompleted":0,
                            "QueriesProcessed":0,
                            "UniqueUsers":set()}
          
    def generateReport(self):        
        reportLogs = self.extractReportLines()
        self.countReportEvents(reportLogs)
        return self.generateReportText()
    
    def extractReportLines(self):
        settings.logSemaphore.acquire()
        try:
            f = open(settings.logFile,"r")
            loglines = map(lambda x:x.strip(),f.readlines())
            f.close()
        finally:
            settings.logSemaphore.release()
        for i in range(len(loglines)-1,-1,-1):
            try:
                if time.mktime(time.strptime(str(datetime.date.today().year)+"."+loglines[i][:14],"%Y."+self.logTimeFormat)) < self.currentTime or i == 0:
                    print loglines[i],i
                    break
            except:
                pass
                
        return loglines[i:]
    
    def countReportEvents(self,reportLogs):
        for line in reportLogs:
            if "vislogged" in line:
                self.reportStats["AnalysisCompleted"] += 1                
            if "sends a query" in line:
                self.reportStats["QueriesProcessed"] += 1
            if "Error:" in line:
                self.reportStats["Errors"].append(line)
            if "is about to be allowed to be computed" in line:
                dne = line.split(":")[-1]
                dn = dne[:dne.rfind("is")-1].strip()
                self.reportStats["DatasetsSubmited"].append(dn)
                self.reportStats["DatasetsWaiting"].append(dn)
            if "is now computing" in line:
                dne = line.split(":")[-1]
                dn = dne[:dne.rfind("is")-1].strip()
                try:
                    self.reportStats["DatasetsWaiting"].remove(dn)
                except ValueError:
                    pass
            if "sendUserDatasetNotificationEmail: called with" in line:
                dn = line.split(",")[3].strip()
                self.reportStats["DatasetsComputed"].append(dn)
            if ".XYZ" in line:
                lineParts = line.split(" ")
                for lp in lineParts:
                    if ".XYZ" in lp:
                        self.reportStats["UniqueUsers"].add(lp)
        try:
            self.reportStats["DatasetsQueue"] = self.datasetServer.getDatasetQueueStatus()
        except:
            self.datasetServer = None
            self.reportStats["DatasetsQueue"] = None
                
    def generateReportText(self):
        report = "EpiExplorer report for activity since "+time.strftime(self.logTimeFormat,time.localtime(self.currentTime))+"<br/>\n<br/>\n"
        report += "<b>Summary</b><br/>\n"
        report += "Errors: "+str(len(self.reportStats["Errors"]))+"<br/>\n"
        report += "AnalysisCompleted: "+str(self.reportStats["AnalysisCompleted"])+"<br/>\n"
        report += "QueriesProcessed: "+str(self.reportStats["QueriesProcessed"])+"<br/>\n"
        report += "UniqueUsers: "+str(len(self.reportStats["UniqueUsers"]))+"<br/>\n"
        report += "DatasetsSubmited: "+str(len(self.reportStats["DatasetsSubmited"]))+"<br/>\n"
        report += "DatasetsWaiting: "+str(len(self.reportStats["DatasetsWaiting"]))+"<br/>\n"
        if self.reportStats["DatasetsQueue"] != None:
            report += "DatasetsQueue: "+str(len(self.reportStats["DatasetsQueue"][0]))+", "+str(len(self.reportStats["DatasetsQueue"][1]))+"<br/>\n"
        else:
            report += "DatasetsQueue: Not accessible<br/>\n"
        report += "DatasetsComputed: "+str(len(self.reportStats["DatasetsComputed"]))+"<br/>\n"
        report += "<br/>\n<br/>\n<b>Details</b><br/>\n"
        if len(self.reportStats["Errors"]) > 0:
            report += "Errors<br/>\n<ul><li>"
            report += "</li><br/>\n<li>".join(self.reportStats["Errors"])
            report += "</li></ul>"
        if len(self.reportStats["DatasetsSubmited"]) + len(self.reportStats["DatasetsWaiting"]) + len(self.reportStats["DatasetsComputed"]) > 0: 
            report += "<br/>\nDatasets\n<br/>"
            if len(self.reportStats["DatasetsSubmited"]) > 0:
                report += "<li>DatasetsSubmited: "+str(", ".join(self.reportStats["DatasetsSubmited"]))+"</li><br/>\n"
            if len(self.reportStats["DatasetsWaiting"]) > 0:
                report += "<li>DatasetsWaiting: "+str(", ".join(self.reportStats["DatasetsWaiting"]))+"</li><br/>\n"
            if self.reportStats["DatasetsQueue"] != None and (len(self.reportStats["DatasetsQueue"][0])+len(self.reportStats["DatasetsQueue"][1])) > 0:
                report += "<li>DatasetsQueue: "+str(", ".join(self.reportStats["DatasetsQueue"][0]))+" :: "+str(", ".join(self.reportStats["DatasetsQueue"][1]))+"</li><br/>\n"
            if len(self.reportStats["DatasetsComputed"]) > 0:
                report += "<li>DatasetsComputed: "+str(", ".join(self.reportStats["DatasetsComputed"]))+"</li><br/>\n"
        report += "</ul>REPORT END"
        return report
    
    def setReportStartTime(self,t):
        # for testing purposes
        self.currentTime = t
        
    def getRemainingTimeUntilNextEvent(self,hour,minute):        
        ct = time.time()
        ctd = list(time.localtime(ct))
        ctd[3:6] = [hour,minute,0] #make the report at 6:00:00 each morning
        tsn = time.struct_time(ctd)
        nt = time.mktime(tsn)
        
        while nt <= ct:
            nt += settings.CS_TIME_REPORT_TIME
        return int(nt - ct)
        
                
        
        

if __name__ == "__main__":
    rm = ReportManager(None)
    
    print rm.getRemainingTimeUntilNextEvent(6,0)
    print rm.getRemainingTimeUntilNextEvent(10,0)
    
    rm.setReportStartTime(rm.currentTime - settings.CS_TIME_REPORT_TIME)
    print rm.generateReport()
    rm.setReportStartTime(rm.currentTime - 2*settings.CS_TIME_REPORT_TIME)
    print rm.generateReport()