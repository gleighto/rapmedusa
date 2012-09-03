import rapmedusa
import redis
import unittest

from rapmedusa import emit, getMapReduceManager

class MapReduceTestCase(unittest.TestCase):

   
    def setUp(self):
        self.data = [{'id': 1, 'tags': ['red', 'green']},
                     {'id': 2, 'tags': ['green']},
                     {'id': 3, 'tags': ['blue', 'green']}]
        
        self.inKey = 'mr_input'
        self.sortKey = 'mr_sort'
        self.sortedKeySet = 'mr_sorted_keys'
        self.outKey = 'mr_output'
        self.conn = redis.StrictRedis(host='localhost',port=6379,db=0)
        
        index = 0
        for entry in self.data:
            for tag in entry['tags']:
                self.conn.hset(self.inKey, index, tag)
                index += 1

    def tearDown(self):
        self.conn.delete(self.inKey)
        getMapReduceManager().cleanUp()
        self.conn.delete(self.outKey)

    def mapFn(self, k, v):
        emit(v, 1)

    def reduceFn(self, key, vals):
        total = 0

        for v in vals:
            total += int(v)

        return total
    
    def test_map_reduce(self):
        rapmedusa.map_reduce(self.conn,
                            self.mapFn,
                            self.reduceFn,
                            self.inKey,
                            self.sortKey,
                            self.sortedKeySet,
                            self.outKey,
                            False)

        
        # after creating buckets according to map output keys, does the
        # result match what we expect?
        self.assertEquals(getMapReduceManager().getMappedVals(),
                          {'mr_sort:green': ['1', '1', '1'],
                           'mr_sort:red': ['1'],
                           'mr_sort:blue': ['1']})

        # check the outputs after running the reduce function
        self.assertEquals(getMapReduceManager().getOutput(),
                          {'blue': '1',
                           'red': '1',
                           'green': '3'})
        
            

        
        
        

    
    
                                         
        
