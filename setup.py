#!/usr/bin/env python

import doctest
import unittest
from setuptools import setup, find_packages


def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # test_suite.addTest(doctest.DocTestSuite('pipeline.queue_tools'))
    # test_suite.addTest(doctest.DocTestSuite('pipeline.pipeline'))
    test_suite.addTest(test_loader.discover('tests', pattern='test_*.py'))
    return test_suite

setup(name='pipeline',
      version='0.1',
      description='Pipelines',
      author='Alex Lemann',
      author_email='alex.lemann@subsetsum.com',
      url='http://subsetsum.com/',
      packages=find_packages(),
      test_suite='setup.test_suite',
      )
