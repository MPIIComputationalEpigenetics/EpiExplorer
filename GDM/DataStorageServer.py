'''
Created on Sep 28, 2012

@author: albrecht
'''

import settings
import time
import sqlite3
import os
import sys
import ThreadedXMLRPCServer

from random import randint
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# TODO(albrecht) put to be called inside the cgsdatasetserver
class DataStorageServer:
    file_types = []

    def __init__(self):
        self.default_dir = settings.exportBaseFolder + "/storage" 
        self.metadata_file = self.default_dir + "/metadata.sqlite3"
        
        if not os.path.exists(self.default_dir):
            os.makedirs(self.default_dir)
        
        if not os.path.exists(self.metadata_file):
            print self.metadata_file            
            conn = sqlite3.connect(self.metadata_file)
            c = conn.cursor()
            c.execute('CREATE TABLE files (name TEXT, software TEXT, format TEXT, internal_id TEXT PRIMARY KEY, create_time DATETIME, total_access INTEGER, last_access DATETIME)')
            conn.commit()
            c.close()
            conn.close()      
                      
    def store_data(self, name, software, data_format, data):
        if not name or len(name) is 0:
            raise InvalidIdentifiarException("name", name)
        millis = int(round(time.time()))
        internal_id = name+"_"+software+"_"+str(millis)+"_"+str(randint(100000,999999))
                
        directory = self.default_dir + "/" + software
        if not os.path.exists(directory):
            # LOG: created directory.
            os.mkdir(directory)
        
        file_path = directory + "/" + internal_id
        self.__save_file(data, file_path)
        self.__store_in_db(name, software, data_format, internal_id, millis)
        
        return internal_id
        
    def retrieve_file(self, software, internal_id):
        file_info = self.__get_file_info(internal_id)

        if not file_info:
            return None
                
        print software
        print file_info["software"]
        if software != file_info["software"]:
            raise Exception("software do not match")
        
        internal_id = file_info["internal_id"]
        
        self.__update_access(internal_id)
        content = self.__read_file_content(software, internal_id)
        return content

    def retrieve_file_as_bed(self, software, internal_id):
        file_info = self.__get_file_info(internal_id)

        if software != file_info["software"]:
            raise Exception("software do not match")

        if file_info["format"] == "BED":
            content = self.__read_file_content(software, internal_id)
        elif file_info["format"] == "BZIP":
            pass
        
        return content

    def list_files(self):
        conn = self.__get_conn()
        c = conn.cursor()
        rows = []    
        for row in c.execute("SELECT name, software, format, internal_id, create_time, total_access, last_access FROM files"):        
            row_dict = {"name":row[0], "software":row[1], "format":row[2], "internal_id":row[3], "create_time": row[4], "total_access": row[5], "last_access":row[6]}
            rows.append(row_dict)
        c.close()
        conn.close()
        
        print rows
        return rows

    # TODO
    def delete_file(self, software, internal_id):
        directory = self.default_dir + "/" + software
        file_path = directory + "/" + internal_id
        
        if not os.path.exists(file_path):
            print "file not found"
            return False
        
        self.__remove_from_db(internal_id)
        os.remove(file_path)
        
        return True

    def __get_file_info(self, internal_id):
        conn = self.__get_conn()
        c = conn.cursor()
        c.execute("SELECT name, software, format, internal_id, create_time, total_access, last_access FROM files WHERE internal_id=?", tuple([internal_id]))
        # TODO: check if found
        row = c.fetchone()
        if not row:
            return None
        
        row_dict = {"name":row[0], "software":row[1], "format":row[2], "internal_id":row[3], "create_time": row[4], "total_access": row[5], "last_access":row[6]}
        c.close()
        conn.close()
        return row_dict
     
    def __save_file(self, data, file_path):
        if os.path.exists(file_path):
            raise FileExistsException(file_path)
        f = open(file_path, "w");
        f.write(data)
        f.close()
        
    def __store_in_db(self, name, software, file_format, internal_id, access_date):
        conn = self.__get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO files VALUES(?,?,?,?,?,?,?)",
            tuple([name, software, file_format, internal_id, access_date, 0, 0]))
        conn.commit()
        c.close()
        conn.close()

    def __read_file_content(self, software, internal_id):
        file_path = self.default_dir + "/" + software + "/" + internal_id
        f = open(file_path, "r");        
        content = f.read()
        f.close()

        return content

    def __update_access(self, internal_id):
        file_info = self.__get_file_info(internal_id)
        if not file_info:
            return
        
        conn= self.__get_conn()
        c = conn.cursor()
        millis = int(round(time.time()))
        c.execute("UPDATE files SET total_access = ?, last_access = ? WHERE internal_id = ?",
            tuple([file_info["total_access"] + 1, millis, internal_id]))
        conn.commit()
        c.close()        
        conn.close()

    def __remove_from_db(self, internal_id):
        conn = self.__get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM files WHERE internal_id=?", tuple([internal_id]))
        conn.commit()
        conn.close()
        
    def __get_conn(self):
        conn = sqlite3.connect(self.metadata_file)
        return conn

    # TODO: implement
    def cleanup(self, unused_since):
        # if not used, delete in one week
        # if is used, keep.
        pass
          
class InvalidIdentifiarException(Exception):
    def __init__(self, field, value):
        self.field = field
        self.value = value
    def __str__(self):
        return "Value "+ repr(self.value) + " for the field " + repr(self.field) + " is invalid."
    
class FileExistsException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "File "+ repr(self.value) + " already exists." 


if __name__ == '__main__':
    dataStorage = DataStorageServer()
    host = "localhost"
    port = 51545
    server = ThreadedXMLRPCServer.ThreadedXMLRPCServer((host, port), SimpleXMLRPCRequestHandler,encoding='ISO-8859-1',allow_none=True)
    server.request_queue_size = 20
    sys.setcheckinterval(30)
    server.register_instance(dataStorage)
    print "The DataStorage XMLRPC-Server runs at host: "+str(host)+", port: "+str(port)+"."
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "blah :("
            
        