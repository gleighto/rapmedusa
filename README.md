# RapMedusa

RapMedusa is a Python module implementing MapReduce querying over a 
Redis key-value store.  It aims to provide functionality that is similar 
(in some respects) to CouchDB's views feature and MongoDB's MapReduce database 
command.

## Dependencies

RapMedusa depends on Andy McCurdy's `redis-py` module, which can be 
obtained from [https://github.com/andymccurdy/redis-py][1]. Of course, 
you'll also need a running [Redis][2] instance to connect to.  In both cases,
any version >= 2.0 should be compatible with RapMedusa.

## Installation

    $ sudo pip install rapmedusa

or

    $ sudo easy_install rapmedusa

or from source:

    $ sudo python setup.py install

## Overview

First, import the required modules:

    :::python
        >>> import redis
        >>> from rapmedusa import emit, map_reduce

Next, connect to a running Redis instance in the usual way:

    :::python
        >>> redis = redis.StrictRedis(host='localhost', port=6379, db=0)

Finally, implementations of the map and reduce functions must be provided, and passed into a call to the map_reduce() function, along with the active connection to the Redis server:

    :::python
        >>> def myMap(key, val):
                ...
                emit(newKey, newVal)

   
        >>> def myReduce(key, values):
                ...
                return newVal

        >>> result = map_reduce(redis, myMap, myReduce)

This returns a Python dictionary object, containing the result of running the MapReduce job.  Each key within the dictionary corresponds to a key passed into the reduce function, and contains the value computed by the reduce function for that key.


## Details

Now it's time to take a deeper look into how RapMedusa carries out a MapReduce job.  There are basically 6 steps:

	1) Read the input data set from a specified Redis hash.
	2) Pass each key/value pair from the input data set to the registered map function.
	3) Organize key/value pairs emitted by the map function into a set of Redis lists, one list per distinct emitted key.
	4) Each of these lists is passed to the registered reduce function, along with the corresponding key.
	5) The result of each call to reduce is stored in the Redis hash reserved for the job output, under the key used in the reduce call.
	6) A Python dictionary representing the contents of the job output hash is returned.
	
A natural question at this point is how are the input and output hash keys specified? These (and other temporary Redis keys used in the 
above steps) can optionally be specified within the call to map_reduce().  Here's a list of the additional, optional parameters that can be 
specified in the call:

	* inKey -- specifies the key under which the input data set is stored (defaults to 'rapmedusa:inputs')
	* outKey -- specifies the key under which the job output is stored (defaults to 'rapmedusa:outputs')
	* sortKey -- specifies the key prefix under which the output of the map function (step 3 above) is stored (defaults to 'rapmedusa:sortedVals')
	* sortedKeySet -- specifies the key under which the set formed from the list keys of step 3 is stored (defaults to 'rapmedusa:sortedKeySet')
	* cleanUp -- a boolean value indicating whether the temporary keys (sortKey, sortedKeySet) should be deleted from the Redis store upon the completion of the MapReduce job (defaults to True)  
	
You'll rarely need to override the default values for sortedKey and sortedKeySet, as a naming conflict is highly unlikely.  You may, however, wish to specify custom values for inKey and outKey that are easier to remember.  


## Examples

### Example 1: Counting Ages

This example demonstrates a MapReduce job in which the input keys are mapped to person records, and the map function generates keys 
based on one of the record entries, `age`.

    :::python
	>>> import redis
	>>> from rapmedusa import *
	
	>>> conn = redis.StrictRedis(host='localhost', port=6379, db=0)
	>>> conn.hset('myInput', 1, "{'name': 'Chad', 'age': 43}")
	>>> conn.hset('myInput', 2, "{'name': 'Ron', 'age': 21}")
	>>> conn.hset('myInput', 3, "{'name': 'George', 'age': 54}")
	>>> conn.hset('myInput', 4, "{'name': 'Alice', 'age': 54}")

	>>> def myMap(key, value):
			obj = eval(value)
			emit(str(obj['age']), '1')

	
	>>> def myReduce(key, vals):
			total = 0
			for v in vals:
				total += int(v)
			return total

	>>> result = map_reduce(conn, myMap, myReduce, inKey='myInput')
	>>> print result
	{'54': '2', '21': '1', '43': '1'}




Author
------

RapMedusa is developed and maintained by Greg Leighton (grleighton@gmail.com).
The most up-to-date version can be downloaded at [https://github.com/gleighto/rapmedusa][3].

[1]: https://github.com/andymccurdy/redis-py
[2]: http://redis.io
[3]: https://github.com/gleighto/rapmedusa
