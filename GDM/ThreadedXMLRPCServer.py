## {{{ http://code.activestate.com/recipes/425043/ (r3)
# Guyon Moree
# http://gumuz.looze.net/

import SocketServer
#import time
from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
 
# Threaded mix-in
class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer): 
    
    def echo(self,msg):
        return  "Threaded echo:"+msg
    
 
## Example class to be published
#class TestObject:
#    def pow(self, x, y):        
#        return pow(x, y)
# 
#    def add(self, x, y) :
#        #time.sleep(20)
#        return x + y
# 
#    def divide(self, x, y):
#        return float(x) / float(y)
 
 
# Instantiate and bind to localhost:8080
#server = ThreadedXMLRPCServer(('', 8099), SimpleXMLRPCRequestHandler)
 
# Register example object instance
#server.register_instance(TestObject())
 
# run!
#server.serve_forever()
## end of http://code.activestate.com/recipes/425043/ }}}
