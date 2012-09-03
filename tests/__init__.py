import unittest

from tests.mapreduce import MapReduceTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MapReduceTestCase))
    return suite
