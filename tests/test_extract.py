# -*- coding: utf-8 -*-
import pytest
from bs4 import BeautifulSoup as BS4Soup

import unittest

from fast_soup import FastSoup


class TestExtractBase(unittest.TestCase):
    __test__ = False
    EXPECTED_VALUE1 = ''
    EXPECTED_VALUE2 = ''

    def test_extract_tag(self):
        soup = self.soup(u'<a>1</a><test>2</test><a>3</a><b>4</b>')
        soup.find('test').extract()
        self.assertEqual(str(soup), self.EXPECTED_VALUE1)

    def test_extract_tag_multiple_tags(self):
        soup = self.soup(u'<a>1</a><test>2</test><a>3</a><test>4</test><b>4</b>')
        soup.find('test').extract()
        self.assertEqual(str(soup), self.EXPECTED_VALUE2)


class TestExtractBS4Soup(TestExtractBase):
    __test__ = True
    EXPECTED_VALUE1 = '<html><body><a>1</a><a>3</a><b>4</b></body></html>'
    EXPECTED_VALUE2 = '<html><body><a>1</a><a>3</a><test>4</test><b>4</b></body></html>'

    def soup(self, markup, **kwargs):
        """Build a Beautiful Soup object from markup."""
        return BS4Soup(markup)


class TestExtractFastSoup(TestExtractBase):
    __test__ = True
    EXPECTED_VALUE1 = '<html><body><a>1</a><a>3</a><b>4</b></body></html>'
    EXPECTED_VALUE2 = '<html><body><a>1</a><a>3</a><test>4</test><b>4</b></body></html>'

    def soup(self, markup, **kwargs):
        """Build a Beautiful Soup object from markup."""
        return FastSoup(markup)
