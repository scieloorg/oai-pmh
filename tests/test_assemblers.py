import unittest
from unittest.mock import patch
from datetime import datetime

from oaipmh import assemblers


class SchemaValidatorMixin:
    def assertXMLIsValid(self, xml_bytes):
        validator = assemblers.OAIValidator(xml_bytes)
        if not validator.validate():
            raise self.failureException('the XML is invalid')


class MakeIdentifyTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.repository = {
            'repositoryName': 'SciELO Brazil',
            'baseURL': 'https://oai.scielo.br/',
            'protocolVersion': '2.0',
            'adminEmail': 'scielo-dev@googlegroups.com',
            'earliestDatestamp': datetime(1909, 4, 1),
            'deletedRecord': 'no',
            'granularity': 'YYYY-MM-DD',
        }
        self.request = {'verb': 'Identify'}

    @patch('oaipmh.filters.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="Identify">https://oai.scielo.br/</request><Identify><repositoryName>SciELO Brazil</repositoryName><baseURL>https://oai.scielo.br/</baseURL><protocolVersion>2.0</protocolVersion><adminEmail>scielo-dev@googlegroups.com</adminEmail><earliestDatestamp>1909-04-01</earliestDatestamp><deletedRecord>no</deletedRecord><granularity>YYYY-MM-DD</granularity></Identify></OAI-PMH>'
        self.assertEqual(expected,
                assemblers.make_identify(self.request, self.repository))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                assemblers.make_identify(self.request, self.repository))


class MakeListMetadataFormatsTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.repository = {
            'repositoryName': 'SciELO Brazil',
            'baseURL': 'https://oai.scielo.br/',
            'protocolVersion': '2.0',
            'adminEmail': 'scielo-dev@googlegroups.com',
            'earliestDatestamp': datetime(1909, 4, 1),
            'deletedRecord': 'no',
            'granularity': 'YYYY-MM-DD',
        }
        self.request = {'verb': 'ListMetadataFormats'}
        self.formats = [
                    {
                        'metadataPrefix': 'oai_dc',
                        'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                        'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                    },
                ]

    @patch('oaipmh.filters.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="ListMetadataFormats">https://oai.scielo.br/</request><ListMetadataFormats><metadataFormat><metadataPrefix>oai_dc</metadataPrefix><schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema><metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace></metadataFormat></ListMetadataFormats></OAI-PMH>'
        self.assertEqual(expected,
                assemblers.make_list_metadata_formats(self.request,
                    self.repository, self.formats))

    def test_xml_validity(self):
        self.assertXMLIsValid(
                assemblers.make_list_metadata_formats(self.request,
                    self.repository, self.formats))


class MakeListIdentifiersTests(SchemaValidatorMixin, unittest.TestCase):
    def setUp(self):
        self.repository = {
            'repositoryName': 'SciELO Brazil',
            'baseURL': 'https://oai.scielo.br/',
            'protocolVersion': '2.0',
            'adminEmail': 'scielo-dev@googlegroups.com',
            'earliestDatestamp': datetime(1909, 4, 1),
            'deletedRecord': 'no',
            'granularity': 'YYYY-MM-DD',
        }
        self.request = {'verb': 'ListMetadataFormats'}
        self.resources = [
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

    @patch('oaipmh.filters.datetime')
    def test_correct_usage(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2017, 6, 22, 19, 1, 43)
        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-06-22T19:01:43Z</responseDate><request verb="ListMetadataFormats">https://oai.scielo.br/</request><ListIdentifiers><header><identifier>oai:arXiv:cs/0112017</identifier><datestamp>2017-06-14</datestamp><setSpec>set1</setSpec><setSpec>set2</setSpec></header></ListIdentifiers></OAI-PMH>'
        self.assertEqual(expected,
                assemblers.make_list_identifiers(self.request,
                    self.repository, self.resources)) 

    def test_xml_validity(self):
        self.assertXMLIsValid(
                assemblers.make_list_identifiers(self.request,
                    self.repository, self.resources)) 

