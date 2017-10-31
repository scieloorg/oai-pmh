import unittest

from oaipmh import (
        entities,
        exceptions,
        )


class ResumptionTokenInterfaceTest:
    def test_responds_to_encode(self):
        self.assertTrue(hasattr(self.object, 'encode'))

    def test_responds_to_decode(self):
        self.assertTrue(hasattr(self.object, 'decode'))

    def test_responds_to_next(self):
        self.assertTrue(hasattr(self.object, 'next'))

    def test_responds_to_new_from_request(self):
        self.assertTrue(hasattr(self.object, 'new_from_request'))

    def test_responds_to_query_offset(self):
        self.assertTrue(hasattr(self.object, 'query_offset'))

    def test_responds_to_query_from(self):
        self.assertTrue(hasattr(self.object, 'query_from'))

    def test_responds_to_query_until(self):
        self.assertTrue(hasattr(self.object, 'query_until'))

    def test_responds_to_query_count(self):
        self.assertTrue(hasattr(self.object, 'query_count'))

    def test_responds_to_is_first_page(self):
        self.assertTrue(hasattr(self.object, 'is_first_page'))


class ResumptionTokenTests(ResumptionTokenInterfaceTest, unittest.TestCase):

    def setUp(self):
        self.object = entities.ChunkedResumptionToken()

    def test_token_is_encoded_correctly(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(0)', count='1000',
                metadataPrefix='oai_dc')
        self.assertEqual(token.encode(),
                ':1998-01-01:1998-12-31:1998-01-01(0):1000:oai_dc')

    def test_encode_ommit_empty_strings(self):
        token = entities.ChunkedResumptionToken(set='', from_='', until='',
                offset='1998-01-01(0)', count='1000', metadataPrefix='oai_dc')
        self.assertEqual(token.encode(),
                ':::1998-01-01(0):1000:oai_dc')

    def test_encode_turns_integer_to_string(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(0)', count=1000,
                metadataPrefix='oai_dc')
        self.assertEqual(token.encode(),
                ':1998-01-01:1998-12-31:1998-01-01(0):1000:oai_dc')

    def test_encode_treats_none_as_empty_strings(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(0)', count=None,
                metadataPrefix='oai_dc')
        self.assertEqual(token.encode(),
                ':1998-01-01:1998-12-31:1998-01-01(0)::oai_dc')

    def test_token_is_decoded_correctly(self):
        token = 'foo:1998-01-01:1998-12-31:1998-01-01(0):1000:oai_dc'
        self.assertEqual(entities.ChunkedResumptionToken.decode(token),
                entities.ChunkedResumptionToken(set='foo', from_='1998-01-01',
                    until='1998-12-31', offset='1998-01-01(0)', count='1000',
                    metadataPrefix='oai_dc'))

    def test_decodes_empty_values_to_empty_strings(self):
        token = ':::1998-01-01(0):1000:oai_dc'
        self.assertEqual(entities.ChunkedResumptionToken.decode(token),
                entities.ChunkedResumptionToken(set='', from_='', until='',
                    offset='1998-01-01(0)', count='1000',
                    metadataPrefix='oai_dc'))

    def test_first_page_detection(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(0)', count='1000',
                metadataPrefix='oai_dc')
        self.assertTrue(token.is_first_page())


    def test_non_first_page_detection(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(100)', count='1000',
                metadataPrefix='oai_dc')
        self.assertFalse(token.is_first_page())

    def test_non_first_page_detection_on_different_from_year(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1999-12-31', offset='1999-01-01(0)', count='1000',
                metadataPrefix='oai_dc')
        self.assertFalse(token.is_first_page())


class ResumptionTokenPrivateMethodTests(unittest.TestCase):
    def test_increments_offset_size(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(0)', count='1000',
                metadataPrefix='oai_dc')
        self.assertEqual(token._incr_offset_size(),
                entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-01-01(1000)', count='1000',
                metadataPrefix='oai_dc'))

    def test_increments_offset_from(self):
        token = entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1998-12-31(1001)', count='1000',
                metadataPrefix='oai_dc')
        self.assertEqual(token._incr_offset_from(),
                entities.ChunkedResumptionToken(set='', from_='1998-01-01',
                until='1998-12-31', offset='1999-01-01(0)', count='1000',
                metadataPrefix='oai_dc'))


class ResumptionTokenSyntaxTests:
    """A validade do formato do token depende do valor do argumento
    ``defaul_count``, passado para a factory ``new_from_request``. Além disso,
    o esquema de validação depende do valor do atributo ``OAIRequest.verb``.

    As subclasses desta devem redefinir os atributos ``verb`` e ``count``
    para que funcionem corretamente.
    """
    verb = NotImplemented
    count = NotImplemented

    def setUp(self):
        def _partial(token):
            oaireq = self.makeOne(resumptionToken=token)
            return entities.ChunkedResumptionToken.new_from_request(
                    oairequest=oaireq, default_count=self.count,
                    default_from='1998-01-01', default_until='1999-11-07')
        self.create = _partial

    def makeOne(self, **kwargs):
        args = {'verb': self.verb, 'identifier': None, 'metadataPrefix': None,
                'set': None, 'resumptionToken': None, 'from_': None,
                'until': None}
        args.update(**kwargs)

        return entities.OAIRequest(**args)


class ListRecordsResumptionTokenTests(ResumptionTokenSyntaxTests, unittest.TestCase):
    verb = 'ListRecords'
    count = 10

    def test_case_1(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_2(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_3(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_4(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_5(self):
        token = 'setname:1998-01-01:1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_6(self):
        token = 'setname:1998-01-01:1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_7(self):
        token = 'setname:1998-01-01:1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_8(self):
        token = 'setname:1998-01-01:1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_9(self):
        token = 'setname:1998-01-01::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_10(self):
        token = 'setname:1998-01-01::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_11(self):
        token = 'setname:1998-01-01::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_12(self):
        token = 'setname:1998-01-01::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_13(self):
        token = 'setname:1998-01-01:::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_14(self):
        token = 'setname:1998-01-01:::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_15(self):
        token = 'setname:1998-01-01::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_16(self):
        token = 'setname:1998-01-01::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_17(self):
        token = 'setname::1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_18(self):
        token = 'setname::1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_19(self):
        token = 'setname::1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_20(self):
        token = 'setname::1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_21(self):
        token = 'setname::1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_22(self):
        token = 'setname::1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_23(self):
        token = 'setname::1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_24(self):
        token = 'setname::1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_25(self):
        token = 'setname:::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_26(self):
        token = 'setname:::0:10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_27(self):
        token = 'setname:::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_28(self):
        token = 'setname:::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_29(self):
        token = 'setname::::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_30(self):
        token = 'setname::::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_31(self):
        token = 'setname:::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_32(self):
        token = 'setname:::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_33(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_34(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_35(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_36(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_37(self):
        token = ':1998-01-01:1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_38(self):
        token = ':1998-01-01:1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_39(self):
        token = ':1998-01-01:1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_40(self):
        token = ':1998-01-01:1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_41(self):
        token = ':1998-01-01::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_42(self):
        token = ':1998-01-01::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_43(self):
        token = ':1998-01-01::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_44(self):
        token = ':1998-01-01::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_45(self):
        token = ':1998-01-01:::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_46(self):
        token = ':1998-01-01:::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_47(self):
        token = ':1998-01-01::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_48(self):
        token = ':1998-01-01::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_49(self):
        token = '::1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_50(self):
        token = '::1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_51(self):
        token = '::1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_52(self):
        token = '::1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_53(self):
        token = '::1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_54(self):
        token = '::1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_55(self):
        token = '::1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_56(self):
        token = '::1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_57(self):
        token = ':::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_58(self):
        token = ':::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_59(self):
        token = ':::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_60(self):
        token = ':::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_61(self):
        token = '::::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_62(self):
        token = '::::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_63(self):
        token = ':::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_64(self):
        token = ':::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)


class ListIdentifiersResumptionTokenTests(ResumptionTokenSyntaxTests, unittest.TestCase):
    verb = 'ListIdentifiers'
    count = 10

    def test_case_1(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_2(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_3(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_4(self):
        token = 'setname:1998-01-01:1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_5(self):
        token = 'setname:1998-01-01:1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_6(self):
        token = 'setname:1998-01-01:1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_7(self):
        token = 'setname:1998-01-01:1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_8(self):
        token = 'setname:1998-01-01:1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_9(self):
        token = 'setname:1998-01-01::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_10(self):
        token = 'setname:1998-01-01::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_11(self):
        token = 'setname:1998-01-01::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_12(self):
        token = 'setname:1998-01-01::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_13(self):
        token = 'setname:1998-01-01:::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_14(self):
        token = 'setname:1998-01-01:::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_15(self):
        token = 'setname:1998-01-01::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_16(self):
        token = 'setname:1998-01-01::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_17(self):
        token = 'setname::1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_18(self):
        token = 'setname::1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_19(self):
        token = 'setname::1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_20(self):
        token = 'setname::1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_21(self):
        token = 'setname::1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_22(self):
        token = 'setname::1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_23(self):
        token = 'setname::1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_24(self):
        token = 'setname::1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_25(self):
        token = 'setname:::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_26(self):
        token = 'setname:::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_27(self):
        token = 'setname:::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_28(self):
        token = 'setname:::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_29(self):
        token = 'setname::::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_30(self):
        token = 'setname::::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_31(self):
        token = 'setname:::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_32(self):
        token = 'setname:::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_33(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_34(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_35(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_36(self):
        token = ':1998-01-01:1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_37(self):
        token = ':1998-01-01:1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_38(self):
        token = ':1998-01-01:1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_39(self):
        token = ':1998-01-01:1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_40(self):
        token = ':1998-01-01:1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_41(self):
        token = ':1998-01-01::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_42(self):
        token = ':1998-01-01::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_43(self):
        token = ':1998-01-01::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_44(self):
        token = ':1998-01-01::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_45(self):
        token = ':1998-01-01:::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_46(self):
        token = ':1998-01-01:::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_47(self):
        token = ':1998-01-01::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_48(self):
        token = ':1998-01-01::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_49(self):
        token = '::1998-12-31:1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_50(self):
        token = '::1998-12-31:1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_51(self):
        token = '::1998-12-31:1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_52(self):
        token = '::1998-12-31:1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_53(self):
        token = '::1998-12-31::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_54(self):
        token = '::1998-12-31::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_55(self):
        token = '::1998-12-31:::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_56(self):
        token = '::1998-12-31:::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_57(self):
        token = ':::1998-01-01(0):10:oai_dc'
        self.create(token)

    def test_case_58(self):
        token = ':::1998-01-01(0):10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_59(self):
        token = ':::1998-01-01(0)::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_60(self):
        token = ':::1998-01-01(0)::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_61(self):
        token = '::::10:oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_62(self):
        token = '::::10:'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_63(self):
        token = ':::::oai_dc'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

    def test_case_64(self):
        token = ':::::'
        self.assertRaises(exceptions.BadResumptionTokenError, self.create, token)

