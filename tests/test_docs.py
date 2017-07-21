import unittest
import doctest
import pipeline

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(pipeline))
    return tests

if __name__ == '__main__':
    unittest.main()
