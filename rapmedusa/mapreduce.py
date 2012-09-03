import globalvars

from string import rfind


def map_reduce(redis,
               mapFunc,
               reduceFunc,
               inKey='rapmedusa:inputs',
               sortKey='rapmedusa:sortedVals',
               sortedKeySet = 'rapmedusa:sortedKeySet',
               outKey='rapmedusa:outputs',
               cleanUp=True):
    """Performs a MapReduce job and returns the output.

    Keyword arguments:
    redis -- connection to a Redis instance
    mapFunc -- map function to be used in the MapReduce job
    reduceFunc -- reduce function to be used in the MapReduce job
    inKey -- Redis key under which input data set is stored 
    sortKey -- Redis key under which map phase output will
               be stored
    sortedKeySet -- Redis key under which partition list keys will be stored
    outKey -- Redis key under which output of the MapReduce job is stored
    cleanUp -- if True, deletes mapKey, sortKey, sortedKeySet, and outKey from
               Redis after the MapReduce job completes
    """
    
    globalvars.manager = MapReduceManager(redis,
                                          mapFunc,
                                          reduceFunc,
                                          inKey,
                                          sortKey,
                                          sortedKeySet,
                                          outKey)
    globalvars.manager.mapReduce()

    if cleanUp == True:
        globalvars.manager.cleanUp()

    return globalvars.manager.getOutput()

def emit(key, val):
    """Adds a <key, value> pair to the mapped output."""
    globalvars.manager.emitEntry(key, val)

def getMapReduceManager():
    """Returns a reference to the active MapReduceManager instance."""
    return globalvars.manager
    

class MapReduceManager(object):
    """Manages the various phases of a MapReduce job.

    This class handles communication with the Redis instance, invoking the
    Redis commands needed to perform computations at each phase.
    """
    
    def __init__(self,
                 redis,
                 mapFunc,
                 reduceFunc,
                 inKey,
                 sortKey,
                 sortedKeySet,
                 outKey):
        self.mapFunc = mapFunc
        self.reduceFunc = reduceFunc
        self.inKey = inKey
        self.sortKey = sortKey
        self.outKey = outKey
        self.sortedKeySet = sortedKeySet
        self.conn = redis


    def mapReduce(self):
        """Starts the MapReduce job."""
        
        # apply the map function to each key/value in the input
        for key in self.conn.hkeys(self.inKey):
            val = self.conn.hget(self.inKey, key)
            self.mapFunc(key, val)

        # apply the reduce function to each bucket created by the
        # map function
        for sortKey in self.conn.smembers(self.sortedKeySet):
            vals = self.conn.lrange(sortKey, 0, -1)
            newKey = self.__stripKey(sortKey)
            self.conn.hset(self.outKey, newKey,
                           self.reduceFunc(newKey, vals))

    def cleanUp(self):
        """Delete temporary keys from Redis."""
        for sortKey in self.conn.smembers(self.sortedKeySet):
            self.conn.delete(sortKey)

        self.conn.delete(self.sortedKeySet)
            
        
    def emitEntry(self, key, val):
        """Inserts a <key, val> pair in the Redis hash located at sortKey."""
        newKey = newKey = self.__buildKey(self.sortKey, key)
        self.conn.rpush(newKey, val)

        # store a set of the generated sorted key names to facilitate
        # later lookup and deletion
        self.conn.sadd(self.sortedKeySet, newKey)

    
    def getMappedVals(self):
        """Returns the result of the map phase, as a dictionary."""
        result = {}

        for sortKey in self.conn.smembers(self.sortedKeySet):
            result[sortKey] = self.conn.lrange(sortKey, 0, -1)

        return result

    def getOutput(self):
        """Returns a dictionary containing the result of the MapReduce job."""
        result = {}

        for key in self.conn.hkeys(self.outKey):
            result[key] = self.conn.hget(self.outKey, key)

        return result
        

    def __stripKey(self, key):
        return key[rfind(key, ':') + 1:]

    def __buildKey(self, prefix, key):
        return prefix + ':' + key



