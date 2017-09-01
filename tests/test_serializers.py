import unittest
from unittest.mock import patch
from datetime import datetime

from oaipmh import serializers, validators, formatters


class SchemaValidatorMixin:
    def assertXMLIsValid(self, xml_bytes):
        validator = validators.OAIValidator(xml_bytes)
        is_valid, errors = validator.validate()
        if not is_valid:
            raise self.failureException('the XML is invalid: %s' % errors)


class MakeIdentifyTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.data = {
            'repository': {
                'repositoryName': 'SciELO Brazil',
                'baseURL': 'https://oai.scielo.br/',
                'protocolVersion': '2.0',
                'adminEmail': 'scielo-dev@googlegroups.com',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'no',
                'granularity': 'YYYY-MM-DD',
            },
            'request': {'verb': 'Identify'},
        }

    @patch('oaipmh.serializers.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="Identify">https://oai.scielo.br/</request><Identify><repositoryName>SciELO Brazil</repositoryName><baseURL>https://oai.scielo.br/</baseURL><protocolVersion>2.0</protocolVersion><adminEmail>scielo-dev@googlegroups.com</adminEmail><earliestDatestamp>1909-04-01</earliestDatestamp><deletedRecord>no</deletedRecord><granularity>YYYY-MM-DD</granularity></Identify></OAI-PMH>'
        self.assertEqual(expected,
                serializers.serialize_identify(self.data))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                serializers.serialize_identify(self.data))


class MakeListMetadataFormatsTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.data = {
            'repository': {
                'repositoryName': 'SciELO Brazil',
                'baseURL': 'https://oai.scielo.br/',
                'protocolVersion': '2.0',
                'adminEmail': 'scielo-dev@googlegroups.com',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'no',
                'granularity': 'YYYY-MM-DD',
            },
            'request': {'verb': 'ListMetadataFormats'},
            'formats': [
                {
                    'metadataPrefix': 'oai_dc',
                    'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                    'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                },
            ]
        }

    @patch('oaipmh.serializers.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="ListMetadataFormats">https://oai.scielo.br/</request><ListMetadataFormats><metadataFormat><metadataPrefix>oai_dc</metadataPrefix><schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema><metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace></metadataFormat></ListMetadataFormats></OAI-PMH>'
        self.assertEqual(expected,
                serializers.serialize_list_metadata_formats(self.data))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                serializers.serialize_list_metadata_formats(self.data))


class MakeListIdentifiersTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.data = {
            'repository': {
                'repositoryName': 'SciELO Brazil',
                'baseURL': 'https://oai.scielo.br/',
                'protocolVersion': '2.0',
                'adminEmail': 'scielo-dev@googlegroups.com',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'no',
                'granularity': 'YYYY-MM-DD',
            },
            'request': {'verb': 'ListIdentifiers'},
            'resources': [
                {
                    'ridentifier': 'oai:arXiv:cs/0112017',
                    'datestamp': datetime(2017, 6, 14),
                    'setspec': ['set1', 'set2'],
                    'title': [('en', 'MICROBIAL COUNTS OF DARK RED...')],
                    'creator': ['Vieira, Francisco Cleber Sousa'],
                    'subject': [('en', 'bacteria'), ('pt', 'bactéria')],
                    'description': [('en', 'The number of colony forming units (CFU)...')],
                    'publisher': ['Sociedade Brasileira de Microbiologia'],
                    'contributor': ['Evans, R. J.'],
                    'date': ['1998-09-01'],
                    'type': ['research-article'],
                    'format': ['text/html'],
                    'identifier': ['https://ref.scielo.org/7vy47j'],
                    'source': ['Revista de Microbiologia v.29 n.3 1998'],
                    'language': ['en'],
                    'relation': [],
                    'rights': ['http://creativecommons.org/licenses/by-nc/4.0/'],
                },
            ]
        }

    @patch('oaipmh.serializers.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="ListIdentifiers">https://oai.scielo.br/</request><ListIdentifiers><header><identifier>oai:arXiv:cs/0112017</identifier><datestamp>2017-06-14</datestamp><setSpec>set1</setSpec><setSpec>set2</setSpec></header><resumptionToken></resumptionToken></ListIdentifiers></OAI-PMH>'
        self.assertEqual(expected,
                serializers.serialize_list_identifiers(self.data))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                serializers.serialize_list_identifiers(self.data))


class MakeListRecordsTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.data = {
            'repository': {
                'repositoryName': 'SciELO Brazil',
                'baseURL': 'https://oai.scielo.br/',
                'protocolVersion': '2.0',
                'adminEmail': 'scielo-dev@googlegroups.com',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'no',
                'granularity': 'YYYY-MM-DD',
            },
            'request': {'verb': 'ListRecords'},
            'resources': [
                {
                    'ridentifier': 'oai:arXiv:cs/0112017',
                    'datestamp': datetime(2017, 6, 14),
                    'setspec': ['set1', 'set2'],
                    'title': [('en', 'MICROBIAL COUNTS OF DARK RED...')],
                    'creator': ['Vieira, Francisco Cleber Sousa'],
                    'subject': [('en', 'bacteria'), ('pt', 'bactéria')],
                    'description': [('en', 'The number of colony forming units (CFU)...')],
                    'publisher': ['Sociedade Brasileira de Microbiologia'],
                    'contributor': ['Evans, R. J.'],
                    'date': [datetime(1998, 9, 1)],
                    'type': ['research-article'],
                    'format': ['text/html'],
                    'identifier': ['https://ref.scielo.org/7vy47j'],
                    'source': ['Revista de Microbiologia v.29 n.3 1998'],
                    'language': ['en'],
                    'relation': [],
                    'rights': ['http://creativecommons.org/licenses/by-nc/4.0/'],
                },
            ]
        }

    @patch('oaipmh.serializers.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="ListRecords">https://oai.scielo.br/</request><ListRecords><record><header><identifier>oai:arXiv:cs/0112017</identifier><datestamp>2017-06-14</datestamp><setSpec>set1</setSpec><setSpec>set2</setSpec></header><metadata><oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"><dc:title>MICROBIAL COUNTS OF DARK RED...</dc:title><dc:creator>Vieira, Francisco Cleber Sousa</dc:creator><dc:contributor>Evans, R. J.</dc:contributor><dc:description>The number of colony forming units (CFU)...</dc:description><dc:subject>bacteria</dc:subject><dc:subject>bact\xc3\xa9ria</dc:subject><dc:publisher>Sociedade Brasileira de Microbiologia</dc:publisher><dc:date>1998-09-01</dc:date><dc:type>research-article</dc:type><dc:source>Revista de Microbiologia v.29 n.3 1998</dc:source><dc:format>text/html</dc:format><dc:identifier>https://ref.scielo.org/7vy47j</dc:identifier><dc:rights>http://creativecommons.org/licenses/by-nc/4.0/</dc:rights><dc:language>en</dc:language></oai_dc:dc></metadata></record><resumptionToken></resumptionToken></ListRecords></OAI-PMH>'
        self.assertEqual(expected,
                serializers.serialize_list_records(self.data, formatters.oai_dc.make_metadata))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                serializers.serialize_list_records(self.data, formatters.oai_dc.make_metadata))


class MakeGetRecordTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.data = {
            'repository': {
                'repositoryName': 'SciELO Brazil',
                'baseURL': 'https://oai.scielo.br/',
                'protocolVersion': '2.0',
                'adminEmail': 'scielo-dev@googlegroups.com',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'no',
                'granularity': 'YYYY-MM-DD',
            },
            'request': {'verb': 'GetRecord'},
            'resources': [
                {
                    'ridentifier': 'oai:arXiv:cs/0112017',
                    'datestamp': datetime(2017, 6, 14),
                    'setspec': ['set1', 'set2'],
                    'title': [('en', 'MICROBIAL COUNTS OF DARK RED...')],
                    'creator': ['Vieira, Francisco Cleber Sousa'],
                    'subject': [('en', 'bacteria'), ('pt', 'bactéria')],
                    'description': [('en', 'The number of colony forming units (CFU)...')],
                    'publisher': ['Sociedade Brasileira de Microbiologia'],
                    'contributor': ['Evans, R. J.'],
                    'date': [datetime(1998, 9, 1)],
                    'type': ['research-article'],
                    'format': ['text/html'],
                    'identifier': ['https://ref.scielo.org/7vy47j'],
                    'source': ['Revista de Microbiologia v.29 n.3 1998'],
                    'language': ['en'],
                    'relation': [],
                    'rights': ['http://creativecommons.org/licenses/by-nc/4.0/'],
                },
            ]
        }

    @patch('oaipmh.serializers.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="GetRecord">https://oai.scielo.br/</request><GetRecord><record><header><identifier>oai:arXiv:cs/0112017</identifier><datestamp>2017-06-14</datestamp><setSpec>set1</setSpec><setSpec>set2</setSpec></header><metadata><oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"><dc:title>MICROBIAL COUNTS OF DARK RED...</dc:title><dc:creator>Vieira, Francisco Cleber Sousa</dc:creator><dc:contributor>Evans, R. J.</dc:contributor><dc:description>The number of colony forming units (CFU)...</dc:description><dc:subject>bacteria</dc:subject><dc:subject>bact\xc3\xa9ria</dc:subject><dc:publisher>Sociedade Brasileira de Microbiologia</dc:publisher><dc:date>1998-09-01</dc:date><dc:type>research-article</dc:type><dc:source>Revista de Microbiologia v.29 n.3 1998</dc:source><dc:format>text/html</dc:format><dc:identifier>https://ref.scielo.org/7vy47j</dc:identifier><dc:rights>http://creativecommons.org/licenses/by-nc/4.0/</dc:rights><dc:language>en</dc:language></oai_dc:dc></metadata></record></GetRecord></OAI-PMH>'
        self.assertEqual(expected,
                serializers.serialize_get_record(self.data, formatters.oai_dc.make_metadata))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                serializers.serialize_get_record(self.data, formatters.oai_dc.make_metadata))


class MakeListSetsTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.data = {
            'repository': {
                'repositoryName': 'SciELO Brazil',
                'baseURL': 'https://oai.scielo.br/',
                'protocolVersion': '2.0',
                'adminEmail': 'scielo-dev@googlegroups.com',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'no',
                'granularity': 'YYYY-MM-DD',
            },
            'request': {'verb': 'ListSets'},
            'sets': [
                {
                    'setSpec': 'foo',
                    'setName': 'bar',
                },
            ],
        }

    @patch('oaipmh.serializers.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="ListSets">https://oai.scielo.br/</request><ListSets><set><setSpec>foo</setSpec><setName>bar</setName></set><resumptionToken></resumptionToken></ListSets></OAI-PMH>'
        self.assertEqual(expected,
                serializers.serialize_list_sets(self.data))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                serializers.serialize_list_sets(self.data))

