import multiprocessing

class A:    
    y = 6
    def __a__(self,x):        
        print "a",x
        self.y = x
        print "process Y=",self.y
        
    def a(self,x):        
        print "a",x
        self.y = x
        print "process Y=",self.y
    def b(self):
        print "Start b"
        p = multiprocessing.Process(target=self.__a__, args=(7,))        
        p.start()
        print p.name,p.pid, p.is_alive()
        p.join()
        print "Y=",self.y        
        print "End b"


if __name__ == '__main__':
    print "Start main"
    aa = A()
    aa.b()
    print "End main"
