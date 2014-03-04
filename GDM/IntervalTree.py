# the class is taken from 
# http://hackmap.blogspot.com/2008/11/python-interval-tree.html
import operator
#import psyco; psyco.full()
import copy
import numpy

class GenomeIntervalTree:
    def __init__(self, depth=16, minbucket=64, _extent=None, maxbucket=512):        
        self.depth = depth
        self.minbucket = minbucket
        self.extent = _extent
        self.maxbucket = maxbucket                    
        self.chroms = {}
        
#        start = 0
#        for i in xrange(1,len(intervals)):
#            if intervals[i].chrom != intervals[i-1].chrom:
#                stop = i-1                
#                self.chroms[intervals[start].chrom]= IntervalTree(intervals[start:stop+1], depth, minbucket, _extent, maxbucket)
#                #print intervals[start].chrom,start,stop
#                start = i
#        self.chroms[intervals[start].chrom]= IntervalTree(intervals[start:], depth, minbucket, _extent, maxbucket)
        
    def addChromosomeArray(self,chrom,intervals):
        if self.chroms.has_key(chrom):
            raise Exception, "Data was alreayd uploaded for this chromosome "+chrom
        self.depth = max(self.depth,int(numpy.log(len(intervals))))
        self.chroms[chrom] = IntervalTree(intervals,
                                          self.depth, 
                                          self.minbucket, 
                                          self.extent, 
                                          self.maxbucket)
         
        
    def find(self, chrom, start, stop):
        if self.chroms.has_key(chrom):
            overlaps = self.chroms[chrom].find(start, stop)
            overlaps.sort(key=operator.attrgetter('start'))
        else:
            overlaps = []
        return overlaps
    
#    def getNearNonOverlapingInterval(self,overlapping,start,stop):
#        return self.chroms[chrom].getNearNonOverlapingInterval(overlapping,start,stop)
    def getSmallestStart(self,chrom,position):
        if self.chroms.has_key(chrom):
            return self.chroms[chrom].getSmallestStart(position)
        else:
            return None
            
    
    def getLargestStop(self,chrom,position):
        if self.chroms.has_key(chrom):
            return self.chroms[chrom].getLargestStop(position)
        else:
            return None
    
    def cleanup(self):
        for chrom in self.chroms.keys():
            del self.chroms[chrom]
        
            
        
class IntervalTree(object):
    __slots__ = ('intervals', 'left', 'right', 'center', 'minStart', 'maxStop')

    def __init__(self, intervals, depth=16, minbucket=64, _extent=None, maxbucket=512):
        """\
        `intervals` a list of intervals *with start and stop* attributes.
        `depth`     the depth of the tree
        `minbucket` if any node in the tree has fewer than minbucket
                    elements, make it a leaf node
        `maxbucket` even it at specifined `depth`, if the number of intervals >
                    maxbucket, split the node, make the tree deeper.

        depth and minbucket usually do not need to be changed. if
        dealing with large numbers (> 1M) of intervals, the depth could
        be increased to 24.

        Useage:

         >>> ivals = [Interval(2, 3), Interval(1, 8), Interval(3, 6)]
         >>> tree = IntervalTree(ivals)
         >>> sorted(tree.find(1, 2))
         [Interval(2, 3), Interval(1, 8)]

        this provides an extreme and satisfying performance improvement
        over searching manually over all 3 elements in the list (like
        a sucker). 

        the IntervalTree class now also supports the iterator protocol
        so it's easy to loop over all elements in the tree:

         >>> import operator
         >>> sorted([iv for iv in tree], key=operator.attrgetter('start'))
         [Interval(1, 8), Interval(2, 3), Interval(3, 6)]


        NOTE: any object with start and stop attributes can be used
        in the incoming intervals list.
        """ 

        depth -= 1
        if (depth == 0 or len(intervals) < minbucket) and len(intervals) > maxbucket:
            self.intervals = intervals
            self.minStart = None
            self.maxStop = None
            if len(self.intervals) > 0:
                self.minStart = self.intervals[0]
                self.maxStop = self.intervals[0]
                for i in self.intervals:
                    if self.maxStop.stop < i.stop:
                        self.maxStop = i 
            
            self.left = self.right = None
            return 

        
        # sorting the first time through allows it to get
        # better performance in searching later.
        lIntervals = len(intervals)
        intervals.sort(key=operator.attrgetter('start'))
        #===================================================================
        # intervalsStop = copy.copy(intervals)
        # intervalsStop.sort(key=operator.attrgetter('stop'))
        # for i in xrange(len(intervals)):
        #    if i > 0:
        #        intervalsStop[i].prevEnd = intervalsStop[i-1]
        #    else:
        #        intervalsStop[i].prevEnd = None
        #    if i < lIntervals - 1:
        #        intervals[i].nextStart = intervals[i+1]
        #    else:
        #        intervals[i].nextStart = None
        #===================================================================
                
                  

        left = intervals[0].start
        self.minStart = intervals[0]
        self.maxStop = intervals[0]
        right = intervals[0].stop
        for i in intervals:
            if right < i.stop:                
                right = i.stop
                self.maxStop = i
        #center = intervals[len(intervals)/ 2].stop
        center = (left + right) / 2.0

        
        self.intervals = []
        lefts, rights  = [], []
        

        for interval in intervals:
            if interval.stop < center:
                lefts.append(interval)
            elif interval.start > center:
                rights.append(interval)
            else: # overlapping.
                self.intervals.append(interval)
#        self.minStart = None
#        self.maxStop = None
#        for i in self.intervals:
#            if not self.minStart or self.minStart.start > self.intervals[i].start:
#                self.minStart = self.intervals[i]
#            if not self.maxStop or self.maxStop.stop < self.intervals[i].stop:
#                self.maxStop = self.intervals[i]
                 
            
                
        self.left   = lefts  and IntervalTree(lefts,  depth, minbucket, (intervals[0].start,  center)) or None
        self.right  = rights and IntervalTree(rights, depth, minbucket, (center,               right)) or None
        self.center = center
 
 
    def find(self, start, stop):
        """find all elements between (or overlapping) start and stop"""
        if self.intervals and not stop < self.intervals[0].start:
            overlapping = [i for i in self.intervals if i.stop >= start 
                                                    and i.start < stop]
        else:
            overlapping = []

        if self.left and start <= self.center:
            overlapping += self.left.find(start, stop)

        if self.right and stop >= self.center:
            overlapping += self.right.find(start, stop)
            
        return overlapping
    
    def getSmallestStart(self,position):
        if position > self.center:
            if self.right:
                if self.right.minStart.start >= position:
                    return self.right.minStart
                else:
                    return self.right.getSmallestStart(position)
            else:
                return None
        else:# position <= self.center:
            currentBest = None
            for interval in self.intervals:
                if position <= interval.start:                    
                    currentBest = interval
                    break
            if not currentBest:
                if self.left:
                    leftBest = self.left.getSmallestStart(position)
                    if leftBest:
                        return leftBest
                    else:
                        if self.right:
                             return self.right.minStart
                        else:
                            return None
                else:
                    return None
            else:
                if self.left:
                    leftBest = self.left.getSmallestStart(position)
                    if leftBest:
                        if leftBest.start < currentBest.start:
                            return leftBest
                        else:
                            return currentBest
                    else: 
                        return currentBest
                else:
                    return currentBest
         
    
    def getLargestStop(self,position):
#        print "Enter",position,self.center
        if position < self.center:
#            print "position < center"
            if self.left:
#                print "has left"
                if self.left.maxStop.stop < position:
                    return self.left.maxStop
                else:
                    return self.left.getLargestStop(position)
            else:
                return None
        else:#position >= self.center:
#            print "position > center"
            currentBest = None
            for interval in self.intervals:
                if position > interval.stop:
                    if not currentBest or currentBest.stop < interval.stop:                     
                        currentBest = interval            
            if not currentBest:                
                if self.right:
#                    print "has right"
                    rightBest = self.right.getLargestStop(position)
                    if rightBest:
#                        print "has right bets",rightBest.stop
                        return rightBest
                    else:                        
                        if self.left:
#                            print "has left best",self.left.maxStop
                            return self.left.maxStop
                        else:
                            return None
                else:
                    return None
            else:
#                print "currentBest",currentBest.stop
                if self.right:
#                    print "has right"
                    rightBest = self.right.getLargestStop(position)
                    if rightBest:
#                        print "has right best"
                        if rightBest.stop > currentBest.stop:
#                            print "has right best better",rightBest.stop
                            return rightBest
                        else:
                            return currentBest
                    else: 
                        return currentBest
                else:
                    return currentBest
                    
    
    #===========================================================================
    # def getNearNonOverlapingInterval(self,overlapping,start,stop):
    #    next = None
    #    prev = None        
    #    for o in overlapping:
    #        if o.nextStart and o.nextStart.start > stop:
    #            if next:                
    #                if o.nextStart.start < next.start:
    #                    next = o.nextStart
    #            else:
    #                next = o.nextStart
    #        if o.prevEnd and o.prevEnd.stop < start:
    #            if prev:
    #                if o.prevEnd.stop > prev.stop:
    #                    prev = o.prevEnd
    #            else:
    #                prev = o.prevEnd
    #    return (prev,next)
    #===========================================================================
        

    def __iter__(self):
        if self.left:
            for l in self.left: yield l

        for i in self.intervals: yield i

        if self.right:
            for r in self.right: yield r
   
    # methods to allow un/pickling (by pzs):
    def __getstate__(self):
        return { 'intervals' : self.intervals,
                    'left'   : self.left,
                    'right'  : self.right,
                    'center' : self.center }

    def __setstate__(self, state):
        for key,value in state.iteritems():
            setattr(self, key, value)

#class Interval(object):
#    __slots__ = ('start', 'stop')
#    def __init__(self, start, stop):
#        self.start = start
#        self.stop  = stop
#    def __repr__(self):
#        return "Interval(%i, %i)" % (self.start, self.stop)
#    
#    def __getstate__(self):
#        return {'start': self.start, 
#                'stop': self.stop }
#    def __setstate__(self, state):
#        for k, v in state.iteritems():
#            setattr(self, k, v)

class Interval:
    def __init__(self,regionData):
        self.chrom = regionData[0]
        self.start = regionData[1]
        self.stop = regionData[2]
        if len(regionData)> 3:
            self.otherData = regionData[3:]
        
#        self.id = regionData[3]
        
            
    
    def toStr(self):
        return str([self.start,self.stop])
        
        
if __name__ == '__main__':

    def brute_force_find(intervals, start, stop):
        return [i for i in intervals if i.stop >= start and i.start <= stop]

    import random, time
    def rand():
        s = random.randint(1, 2000000)
        return Interval(s, s + random.randint(200, 6000))
    intervals = [rand() for i in xrange(300000)]
    START, STOP = 390000, 400000
    intervals.append(Interval(0, 500000))
    tries = 100

    
    tree = IntervalTree(intervals)
    t = time.time()
    for i in range(tries):
        res = tree.find(START, STOP)
    treetime = time.time() - t
    t = time.time()
    #print treetime

    """

    for i in range(tries):
        bf = [i for i in intervals if i.stop >= START and i.start <= STOP]
    btime = time.time() - t
    assert not set(bf).symmetric_difference(res) , (len(bf), len(res), set(bf).difference(res), START, STOP)
    print treetime, btime, btime/treetime

    
    assert sum(1 for x in tree) == len(intervals), "iterator not working?"

    intervals = [rand() for i in xrange(300)]
    atree = IntervalTree(intervals)
    import cPickle
    btree = cPickle.loads(cPickle.dumps(atree, -1))

    af = atree.find(START, STOP) 
    bf = btree.find(START, STOP)
    assert len(af) == len(bf)
    for a, b in zip(af, bf):
        assert a.start == b.start
        assert a.stop == b.stop
    

    import doctest
    doctest.testmod()
    """
