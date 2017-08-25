import re
import unittest
from collections import namedtuple
import urllib.parse

from .fixtures import factories
from oaipmh import (
        repository,
        datastores,
        sets,
        entities,
        )


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
        token = repository.ResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='0', count='1000',
                metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                ':1998-01-01:1998-12-31:0:1000:oai_dc')

    def test_empty_strings_are_ommited(self):
        token = repository.ResumptionToken(set='', from_='', until='', offset='0',
                count='1000', metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                ':::0:1000:oai_dc')

    def test_integers_became_strings(self):
        token = repository.ResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset=0, count=1000,
                metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                ':1998-01-01:1998-12-31:0:1000:oai_dc')

    def test_nones_became_strings(self):
        token = repository.ResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset=0, count=None,
                metadataPrefix='oai_dc')
        self.assertEqual(repository.encode_resumption_token(token),
                ':1998-01-01:1998-12-31:0::oai_dc')


class decode_resumption_tokenTests(unittest.TestCase):
    def test_only_str_values(self):
        token = ':1998-01-01:1998-12-31:0:1000:oai_dc'
        self.assertEqual(repository.decode_resumption_token(token),
                repository.ResumptionToken(set='', from_='1998-01-01',
                    until='1998-12-31', offset='0', count='1000',
                    metadataPrefix='oai_dc'))

    def test_empty_strings_are_ommited(self):
        token = ':::0:1000:oai_dc'
        self.assertEqual(repository.decode_resumption_token(token),
                repository.ResumptionToken(set='', from_='', until='', offset='0',
                    count='1000', metadataPrefix='oai_dc'))

    def test_integers_became_strings(self):
        token = ':1998-01-01:1998-12-31:0:1000:oai_dc'
        self.assertEqual(repository.decode_resumption_token(token),
                repository.ResumptionToken(set='', from_='1998-01-01',
                    until='1998-12-31', offset='0', count='1000',
                    metadataPrefix='oai_dc'))


class inc_resumption_tokenTests(unittest.TestCase):
    def test_only_offset_advances(self):
        token = repository.ResumptionToken(set='', from_='1998-01-01',
            until='1998-12-31', offset='0', count='1000',
            metadataPrefix='oai_dc')
        self.assertEqual(repository.inc_resumption_token(token),
                repository.ResumptionToken(set='', from_='1998-01-01',
                    until='1998-12-31', offset='1001', count='1000',
                    metadataPrefix='oai_dc'))

    def test_offset_advances_according_to_declared_count(self):
        token = repository.ResumptionToken(set='', from_='1998-01-01',
            until='1998-12-31', offset='0', count='10',
            metadataPrefix='oai_dc')
        self.assertEqual(repository.inc_resumption_token(token),
                repository.ResumptionToken(set='', from_='1998-01-01',
                    until='1998-12-31', offset='11', count='10',
                    metadataPrefix='oai_dc'))


class ListRecordsResumptionTokenRegexpTests(unittest.TestCase):

    def test_case_1(self):
        token = 'setname:1998-01-01:1998-12-31:0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_2(self):
        token = 'setname:1998-01-01:1998-12-31:0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_3(self):
        token = 'setname:1998-01-01:1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_4(self):
        token = 'setname:1998-01-01:1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_5(self):
        token = 'setname:1998-01-01:1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_6(self):
        token = 'setname:1998-01-01:1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_7(self):
        token = 'setname:1998-01-01:1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_8(self):
        token = 'setname:1998-01-01:1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_9(self):
        token = 'setname:1998-01-01::0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_10(self):
        token = 'setname:1998-01-01::0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_11(self):
        token = 'setname:1998-01-01::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_12(self):
        token = 'setname:1998-01-01::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_13(self):
        token = 'setname:1998-01-01:::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_14(self):
        token = 'setname:1998-01-01:::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_15(self):
        token = 'setname:1998-01-01::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_16(self):
        token = 'setname:1998-01-01::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_17(self):
        token = 'setname::1998-12-31:0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_18(self):
        token = 'setname::1998-12-31:0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_19(self):
        token = 'setname::1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_20(self):
        token = 'setname::1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_21(self):
        token = 'setname::1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_22(self):
        token = 'setname::1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_23(self):
        token = 'setname::1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_24(self):
        token = 'setname::1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_25(self):
        token = 'setname:::0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_26(self):
        token = 'setname:::0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_27(self):
        token = 'setname:::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_28(self):
        token = 'setname:::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_29(self):
        token = 'setname::::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_30(self):
        token = 'setname::::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_31(self):
        token = 'setname:::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_32(self):
        token = 'setname:::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_33(self):
        token = ':1998-01-01:1998-12-31:0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_34(self):
        token = ':1998-01-01:1998-12-31:0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_35(self):
        token = ':1998-01-01:1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_36(self):
        token = ':1998-01-01:1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_37(self):
        token = ':1998-01-01:1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_38(self):
        token = ':1998-01-01:1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_39(self):
        token = ':1998-01-01:1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_40(self):
        token = ':1998-01-01:1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_41(self):
        token = ':1998-01-01::0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_42(self):
        token = ':1998-01-01::0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_43(self):
        token = ':1998-01-01::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_44(self):
        token = ':1998-01-01::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_45(self):
        token = ':1998-01-01:::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_46(self):
        token = ':1998-01-01:::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_47(self):
        token = ':1998-01-01::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_48(self):
        token = ':1998-01-01::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_49(self):
        token = '::1998-12-31:0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_50(self):
        token = '::1998-12-31:0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_51(self):
        token = '::1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_52(self):
        token = '::1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_53(self):
        token = '::1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_54(self):
        token = '::1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_55(self):
        token = '::1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_56(self):
        token = '::1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_57(self):
        token = ':::0:10:oai_dc'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_58(self):
        token = ':::0:10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_59(self):
        token = ':::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_60(self):
        token = ':::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_61(self):
        token = '::::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_62(self):
        token = '::::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_63(self):
        token = ':::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))

    def test_case_64(self):
        token = ':::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_RECORDS, token))



class isValidResumptionTokenTests(unittest.TestCase):
    def test_valid(self):
        token = ':1998-01-01:1998-01-01:0:10:oai_dc'
        self.assertTrue(repository.is_valid_resumption_token(token, RES_TOKEN_RECORDS))

    def test_invalid(self):
        token = ':1998-01-01:1998-01-01:0:10:'
        self.assertFalse(repository.is_valid_resumption_token(token, RES_TOKEN_RECORDS))


class ListIdentifiersResumptionTokenRegexpTests(unittest.TestCase):

    def test_case_1(self):
        token = 'setname:1998-01-01:1998-12-31:0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_2(self):
        token = 'setname:1998-01-01:1998-12-31:0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_3(self):
        token = 'setname:1998-01-01:1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_4(self):
        token = 'setname:1998-01-01:1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_5(self):
        token = 'setname:1998-01-01:1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_6(self):
        token = 'setname:1998-01-01:1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_7(self):
        token = 'setname:1998-01-01:1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_8(self):
        token = 'setname:1998-01-01:1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_9(self):
        token = 'setname:1998-01-01::0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_10(self):
        token = 'setname:1998-01-01::0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_11(self):
        token = 'setname:1998-01-01::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_12(self):
        token = 'setname:1998-01-01::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_13(self):
        token = 'setname:1998-01-01:::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_14(self):
        token = 'setname:1998-01-01:::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_15(self):
        token = 'setname:1998-01-01::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_16(self):
        token = 'setname:1998-01-01::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_17(self):
        token = 'setname::1998-12-31:0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_18(self):
        token = 'setname::1998-12-31:0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_19(self):
        token = 'setname::1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_20(self):
        token = 'setname::1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_21(self):
        token = 'setname::1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_22(self):
        token = 'setname::1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_23(self):
        token = 'setname::1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_24(self):
        token = 'setname::1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_25(self):
        token = 'setname:::0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_26(self):
        token = 'setname:::0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_27(self):
        token = 'setname:::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_28(self):
        token = 'setname:::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_29(self):
        token = 'setname::::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_30(self):
        token = 'setname::::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_31(self):
        token = 'setname:::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_32(self):
        token = 'setname:::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_33(self):
        token = ':1998-01-01:1998-12-31:0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_34(self):
        token = ':1998-01-01:1998-12-31:0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_35(self):
        token = ':1998-01-01:1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_36(self):
        token = ':1998-01-01:1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_37(self):
        token = ':1998-01-01:1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_38(self):
        token = ':1998-01-01:1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_39(self):
        token = ':1998-01-01:1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_40(self):
        token = ':1998-01-01:1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_41(self):
        token = ':1998-01-01::0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_42(self):
        token = ':1998-01-01::0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_43(self):
        token = ':1998-01-01::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_44(self):
        token = ':1998-01-01::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_45(self):
        token = ':1998-01-01:::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_46(self):
        token = ':1998-01-01:::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_47(self):
        token = ':1998-01-01::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_48(self):
        token = ':1998-01-01::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_49(self):
        token = '::1998-12-31:0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_50(self):
        token = '::1998-12-31:0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_51(self):
        token = '::1998-12-31:0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_52(self):
        token = '::1998-12-31:0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_53(self):
        token = '::1998-12-31::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_54(self):
        token = '::1998-12-31::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_55(self):
        token = '::1998-12-31:::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_56(self):
        token = '::1998-12-31:::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_57(self):
        token = ':::0:10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_58(self):
        token = ':::0:10:'
        self.assertIsNotNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_59(self):
        token = ':::0::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_60(self):
        token = ':::0::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_61(self):
        token = '::::10:oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_62(self):
        token = '::::10:'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_63(self):
        token = ':::::oai_dc'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))

    def test_case_64(self):
        token = ':::::'
        self.assertIsNone(re.fullmatch(RES_TOKEN_IDENTIFIERS, token))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        meta = factories.get_sample_repositorymeta()
        ds = datastores.InMemory()
        setsreg = sets.SetsRegistry(ds, [])
        self.repository = repository.Repository(meta, ds, setsreg, 10)

    def test_handling_req_with_illegal_args(self):
        req = 'verb=Identify&illegalarg=foo'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"/>'.encode('utf-8') in result)

    def test_handling_req_with_repeated_args(self):
        req = 'verb=Identify&verb=Identify'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"/>'.encode('utf-8') in result)

    def test_handling_req_to_invalid_verb(self):
        req = 'verb=InvalidVerb'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badVerb">'.encode('utf-8') in result)


class oairequest_from_querystringTests(unittest.TestCase):
    def test_verb(self):
        qstr = urllib.parse.parse_qs('verb=ListRecords')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, 'ListRecords')
        self.assertEqual(oairequest.identifier, None)
        self.assertEqual(oairequest.metadataPrefix, None)
        self.assertEqual(oairequest.set, None)
        self.assertEqual(oairequest.resumptionToken, None)
        self.assertEqual(oairequest.from_, None)
        self.assertEqual(oairequest.until, None)

    def test_identifier(self):
        qstr = urllib.parse.parse_qs('identifier=foo')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, None)
        self.assertEqual(oairequest.identifier, 'foo')
        self.assertEqual(oairequest.metadataPrefix, None)
        self.assertEqual(oairequest.set, None)
        self.assertEqual(oairequest.resumptionToken, None)
        self.assertEqual(oairequest.from_, None)
        self.assertEqual(oairequest.until, None)

    def test_metadataprefix(self):
        qstr = urllib.parse.parse_qs('metadataPrefix=foo')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, None)
        self.assertEqual(oairequest.identifier, None)
        self.assertEqual(oairequest.metadataPrefix, 'foo')
        self.assertEqual(oairequest.set, None)
        self.assertEqual(oairequest.resumptionToken, None)
        self.assertEqual(oairequest.from_, None)
        self.assertEqual(oairequest.until, None)

    def test_set(self):
        qstr = urllib.parse.parse_qs('set=foo')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, None)
        self.assertEqual(oairequest.identifier, None)
        self.assertEqual(oairequest.metadataPrefix, None)
        self.assertEqual(oairequest.set, 'foo')
        self.assertEqual(oairequest.resumptionToken, None)
        self.assertEqual(oairequest.from_, None)
        self.assertEqual(oairequest.until, None)

    def test_resumptiontoken(self):
        qstr = urllib.parse.parse_qs('resumptionToken=foo')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, None)
        self.assertEqual(oairequest.identifier, None)
        self.assertEqual(oairequest.metadataPrefix, None)
        self.assertEqual(oairequest.set, None)
        self.assertEqual(oairequest.resumptionToken, 'foo')
        self.assertEqual(oairequest.from_, None)
        self.assertEqual(oairequest.until, None)

    def test_from(self):
        qstr = urllib.parse.parse_qs('from=2017-01-01')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, None)
        self.assertEqual(oairequest.identifier, None)
        self.assertEqual(oairequest.metadataPrefix, None)
        self.assertEqual(oairequest.set, None)
        self.assertEqual(oairequest.resumptionToken, None)
        self.assertEqual(oairequest.from_, '2017-01-01')
        self.assertEqual(oairequest.until, None)

    def test_until(self):
        qstr = urllib.parse.parse_qs('until=2017-01-01')
        oairequest = repository.oairequest_from_querystring(qstr)
        self.assertEqual(oairequest.verb, None)
        self.assertEqual(oairequest.identifier, None)
        self.assertEqual(oairequest.metadataPrefix, None)
        self.assertEqual(oairequest.set, None)
        self.assertEqual(oairequest.resumptionToken, None)
        self.assertEqual(oairequest.from_, None)
        self.assertEqual(oairequest.until, '2017-01-01')

