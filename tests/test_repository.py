import re
import unittest
from collections import namedtuple

from oaipmh import repository


RES_TOKEN_RECORDS = repository.RESUMPTION_TOKEN_PATTERNS['ListRecords']
RES_TOKEN_IDENTIFIERS = repository.RESUMPTION_TOKEN_PATTERNS['ListIdentifiers']


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


class inc_resumption_tokenTests(unittest.TestCase):
    def test_only_offset_advances(self):
        token = repository.ResumptionToken(from_='1998-01-01',
            until='1998-12-31', offset='0', count='1000',
            metadataPrefix='oai_dc')
        self.assertEqual(repository.inc_resumption_token(token),
                repository.ResumptionToken(from_='1998-01-01',
                    until='1998-12-31', offset='1001', count='1000',
                    metadataPrefix='oai_dc'))

    def test_offset_advances_according_to_declared_count(self):
        token = repository.ResumptionToken(from_='1998-01-01',
            until='1998-12-31', offset='0', count='10',
            metadataPrefix='oai_dc')
        self.assertEqual(repository.inc_resumption_token(token),
                repository.ResumptionToken(from_='1998-01-01',
                    until='1998-12-31', offset='11', count='10',
                    metadataPrefix='oai_dc'))


class ListRecordsResumptionTokenRegexpTests(unittest.TestCase):
    def test_case_1(self):
        token = '1998-01-01:1998-01-01:0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_2(self):
        token = '1998-01-01:1998-01-01:0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_3(self):
        token = '1998-01-01:1998-01-01:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_4(self):
        token = '1998-01-01:1998-01-01:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_5(self):
        token = '1998-01-01:1998-01-01::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_6(self):
        token = '1998-01-01:1998-01-01::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_7(self):
        token = '1998-01-01:1998-01-01:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_8(self):
        token = '1998-01-01:1998-01-01:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_9(self):
        token = '1998-01-01::0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_10(self):
        token = '1998-01-01::0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_11(self):
        token = '1998-01-01::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_12(self):
        token = '1998-01-01::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_13(self):
        token = '1998-01-01:::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_14(self):
        token = '1998-01-01:::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_15(self):
        token = '1998-01-01::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_16(self):
        token = '1998-01-01::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_17(self):
        token = ':1998-01-01:0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_18(self):
        token = ':1998-01-01:0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_19(self):
        token = ':1998-01-01:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_20(self):
        token = ':1998-01-01:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_21(self):
        token = ':1998-01-01::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_22(self):
        token = ':1998-01-01::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_23(self):
        token = ':1998-01-01:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_24(self):
        token = ':1998-01-01:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_25(self):
        token = '::0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_26(self):
        token = '::0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_27(self):
        token = '::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_28(self):
        token = '::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_29(self):
        token = ':::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_30(self):
        token = ':::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_31(self):
        token = '::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))
    
    def test_case_32(self):
        token = '::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))


class isValidResumptionTokenTests(unittest.TestCase):
    def test_valid(self):
        token = '1998-01-01:1998-01-01:0:10:oai_dc'
        self.assertTrue(repository.is_valid_resumption_token(token, RES_TOKEN_RECORDS))

    def test_invalid(self):
        token = '1998-01-01:1998-01-01:0:10:'
        self.assertFalse(repository.is_valid_resumption_token(token, RES_TOKEN_RECORDS))


class ListIdentifiersResumptionTokenRegexpTests(unittest.TestCase):
    def test_case_1(self):
        token = '1998-01-01:1998-01-01:0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_2(self):
        token = '1998-01-01:1998-01-01:0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_3(self):
        token = '1998-01-01:1998-01-01:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_4(self):
        token = '1998-01-01:1998-01-01:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_5(self):
        token = '1998-01-01:1998-01-01::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_6(self):
        token = '1998-01-01:1998-01-01::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_7(self):
        token = '1998-01-01:1998-01-01:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_8(self):
        token = '1998-01-01:1998-01-01:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_9(self):
        token = '1998-01-01::0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_10(self):
        token = '1998-01-01::0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_11(self):
        token = '1998-01-01::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_12(self):
        token = '1998-01-01::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_13(self):
        token = '1998-01-01:::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_14(self):
        token = '1998-01-01:::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_15(self):
        token = '1998-01-01::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_16(self):
        token = '1998-01-01::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_17(self):
        token = ':1998-01-01:0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_18(self):
        token = ':1998-01-01:0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_19(self):
        token = ':1998-01-01:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_20(self):
        token = ':1998-01-01:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_21(self):
        token = ':1998-01-01::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_22(self):
        token = ':1998-01-01::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_23(self):
        token = ':1998-01-01:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_24(self):
        token = ':1998-01-01:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_25(self):
        token = '::0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_26(self):
        token = '::0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_27(self):
        token = '::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_28(self):
        token = '::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_29(self):
        token = ':::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_30(self):
        token = ':::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_31(self):
        token = '::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_32(self):
        token = '::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

