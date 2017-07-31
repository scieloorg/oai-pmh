import unittest
from collections import namedtuple

from oaipmh import repository


class asdictTests(unittest.TestCase):
    def test_trailing_underscores_are_stripped(self):
        sample = namedtuple('sample', 'foo_ bar')
        s = sample(foo_='foo value', bar='bar value')

        self.assertEqual(repository.asdict(s),
                {'foo': 'foo value', 'bar': 'bar value'})
    
    def test_many_trailing_underscores_are_stripped(self):
        sample = namedtuple('sample', 'foo__ bar')
        s = sample(foo__='foo value', bar='bar value')

        self.assertEqual(repository.asdict(s),
                {'foo': 'foo value', 'bar': 'bar value'})
    
    def test_underscores_on_values_are_preserved(self):
        sample = namedtuple('sample', 'foo bar')
        s = sample(foo='foo value_', bar='_bar value')

        self.assertEqual(repository.asdict(s),
                {'foo': 'foo value_', 'bar': '_bar value'})

