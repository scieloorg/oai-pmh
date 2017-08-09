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


class encode_resumption_tokenTests(unittest.TestCase):
    def test_only_str_values(self):
        token = repository.ResumptionToken(from_='1998-01-01',
                until='1998-12-31', offset='0', count='1000',
                metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                '1998-01-01:1998-12-31:0:1000:oai_dc')

    def test_empty_strings_are_ommited(self):
        token = repository.ResumptionToken(from_='', until='', offset='0',
                count='1000', metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                '::0:1000:oai_dc')

    def test_integers_became_strings(self):
        token = repository.ResumptionToken(from_='1998-01-01',
                until='1998-12-31', offset=0, count=1000,
                metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                '1998-01-01:1998-12-31:0:1000:oai_dc')

    def test_nones_became_strings(self):
        token = repository.ResumptionToken(from_='1998-01-01',
                until='1998-12-31', offset=0, count=None,
                metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                '1998-01-01:1998-12-31:0::oai_dc')


class decode_resumption_tokenTests(unittest.TestCase):
    def test_only_str_values(self):
        token = '1998-01-01:1998-12-31:0:1000:oai_dc'
        self.assertEqual(repository.decode_resumption_token(token),
                repository.ResumptionToken(from_='1998-01-01',
                    until='1998-12-31', offset='0', count='1000',
                    metadataPrefix='oai_dc'))

    def test_empty_strings_are_ommited(self):
        token = '::0:1000:oai_dc'
        self.assertEqual(repository.decode_resumption_token(token),
                repository.ResumptionToken(from_='', until='', offset='0',
                    count='1000', metadataPrefix='oai_dc'))

    def test_integers_became_strings(self):
        token = '1998-01-01:1998-12-31:0:1000:oai_dc'
        self.assertEqual(repository.decode_resumption_token(token),
                repository.ResumptionToken(from_='1998-01-01',
                    until='1998-12-31', offset='0', count='1000',
                    metadataPrefix='oai_dc'))


class next_resumption_tokenTests(unittest.TestCase):
    def test_only_offset_advances(self):
        token = '1998-01-01:1998-12-31:0:1000:oai_dc'
        self.assertEqual(repository.next_resumption_token(token),
                '1998-01-01:1998-12-31:1001:1000:oai_dc')

    def test_offset_advances_according_to_declared_count(self):
        token = '1998-01-01:1998-12-31:0:10:oai_dc'
        self.assertEqual(repository.next_resumption_token(token),
                '1998-01-01:1998-12-31:11:10:oai_dc')

