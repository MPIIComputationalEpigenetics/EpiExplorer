
import os.path
import sqlite3
import hashlib
import time

import settings
from utilities import *


def recordUserLicense(userData):
    try:
        log("UserHandling.recordUserLicense: Recording user data '"+str(userData)+"'")
        initDB()
        #record the dataset
        conn = sqlite3.connect(settings.userDB)
        c = conn.cursor()
        c.execute('INSERT INTO LicencedUsers VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                  (str(userData["mail"]),
                   str(userData["firstName"]),
                   str(userData["lastName"]),
                   str(userData["institution"]),
                   str(userData["department"]),
                   str(userData["address"]),
                   str(userData["city"]),
                   str(userData["country"]),
                   str(userData["ip"]),
                   str(userData["key"]),
                   gettime())
                   )
        conn.commit()
        c.close()
        conn.close()
    except Exception,ex:
        log("UserHandling.recordUserDataset: ERROR occurred while storing the user info '"+str(ex)+"'")
        return False
    return True

def recordUserDataset(userEmail,datasetSimpleName):
    try:
        log("UserHandling.recordUserDataset: Recording user '"+str(userEmail)+"' and dataset '"+str(datasetSimpleName)+"'")
        initDB()
        #record the dataset
        conn = sqlite3.connect(settings.userDB)
        c = conn.cursor()
        c.execute('INSERT INTO UserDataset VALUES (?,?,?)',(str(userEmail),str(datasetSimpleName),gettime()))
        conn.commit()
        c.close()
        conn.close()
    except Exception,ex:
        log("UserHandling.recordUserDataset: ERROR occurred while storing the user info '"+str(ex)+"'")
        
    
def gettime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
def initDB():
    if not os.path.isfile(settings.userDB):        
        log("UserHandling.initDB: Creating the user tables")
        conn = sqlite3.connect(settings.userDB)    
        try:
            c = conn.cursor()
            c.execute('CREATE TABLE  UserDataset (mail TEXT, datasetName TEXT, time TEXT)')
            c.execute('CREATE TABLE  LicencedUsers (mail TEXT, firstName TEXT, lastName TEXT, institution TEXT, department TEXT, address TEXT, city TEXT, country TEXT, ip TEXT, licenceKey TEXT, time TEXT)')
            conn.commit()
            c.close()
            conn.close()
        except Exception, ex:
            log("UserHandling.initDB: ERROR occurred while creating the user tables '"+str(ex)+"'")
            print ex
            os.unlink(settings.userDB)
            raise ex

            
if __name__ == "__main__":
    initDB()
    recordUserDataset("test@test.com","test dataset")
    userData = {}
    userData["ip"] = "123.123.12.3"
    userData["mail"] = "123"
    userData["firstName"] = "123"
    userData["lastName"] = "123"
    userData["institution"] = "123"
    userData["department"] = "123"
    userData["address"] = "123"
    userData["city"] = "123"
    userData["country"] = "123"
    userData["key"] = "1233"
    recordUserLicense(userData)
