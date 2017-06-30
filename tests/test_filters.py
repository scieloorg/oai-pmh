import unittest
from unittest.mock import patch
from datetime import datetime

from pyramid.registry import Registry
from lxml import etree

from oaipmh import filters


class RootTests(unittest.TestCase):
    def test_returns_pair_of_values(self):
        data = {}
        resp = filters.root(data)

        self.assertEqual(len(resp), 2)

    def test_root_element_tagname(self):
        data = {}
        resp_xml, _ = filters.root(data)
        
        self.assertEqual(resp_xml.tag, 'OAI-PMH')

    def test_root_element_attributes(self):
        data = {}
        resp_xml, _ = filters.root(data)
        
        expected_attrs = {
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd',
                }

        for name, value in expected_attrs.items():
            self.assertEqual(resp_xml.attrib[name], value)


class ResponseDateTests(unittest.TestCase):
    def test_responseDate_element_is_added(self):
        xml = etree.Element('root')
        
        resp_xml, _ = filters.responsedate((xml, {}))
        self.assertEqual(len(resp_xml), 1)
        self.assertEqual(resp_xml[0].tag, 'responseDate')

    @patch('oaipmh.filters.datetime')
    def test_responseDate_is_UTC(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2014, 2, 6, 15, 17, 0)
        xml = etree.Element('root')
        
        resp_xml, _ = filters.responsedate((xml, {}))
        self.assertEqual(resp_xml[0].text, '2014-02-06T15:17:00Z')


class RequestTests(unittest.TestCase):
    def test_request_add_verb_and_base_url(self):
        data = {
            'repository': {'baseURL': 'http://books.scielo.org/oai/'},
            'request': {'verb': 'Identifier'}
        }
        xml = etree.Element('root')
        
        resp_xml, resp_data = filters.request((xml, data))

        xml_str = '<root><request verb="Identifier">http://books.scielo.org/oai/</request></root>'

        self.assertEqual(etree.tostring(resp_xml), xml_str.encode('utf-8'))


class IdentifyTests(unittest.TestCase):

    def test_complete_generation(self):
        data = {
            'repository': {
                'repositoryName': 'SciELO Books',
                'baseURL': 'http://books.scielo.org/oai/',
                'protocolVersion': '2.0',
                'adminEmail': 'books@scielo.org',
                'earliestDatestamp': datetime(1909, 4, 1),
                'deletedRecord': 'persistent',
                'granularity': 'YYYY-MM-DD',
            }
        }
        xml = etree.Element('root')

        resp_xml, _ = filters.identify((xml, data))

        xml_str = '<root>'
        xml_str += '<Identify>'
        xml_str += '<repositoryName>SciELO Books</repositoryName>'
        xml_str += '<baseURL>http://books.scielo.org/oai/</baseURL>'
        xml_str += '<protocolVersion>2.0</protocolVersion>'
        xml_str += '<adminEmail>books@scielo.org</adminEmail>'
        xml_str += '<earliestDatestamp>1909-04-01</earliestDatestamp>'
        xml_str += '<deletedRecord>persistent</deletedRecord>'
        xml_str += '<granularity>YYYY-MM-DD</granularity>'
        xml_str += '</Identify>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(resp_xml), xml_str.encode('utf-8'))


class tobytesTests(unittest.TestCase):

    def test_tobytes_returns_bytes(self):
        data = {}
        xml = etree.Element('root')
        
        resp_xml = filters.tobytes((xml, data))

        self.assertIsInstance(resp_xml, bytes)


class ListMetadataFormatsTests(unittest.TestCase):

    def test_metadata_format_add_info_to_root_element(self):
        data = {
            'formats': [
                {
                    'metadataPrefix': 'prefix',
                    'schema': 'schema',
                    'metadataNamespace': 'namespace'
                }, {
                    'metadataPrefix': 'prefix2',
                    'schema': 'schema2',
                    'metadataNamespace': 'namespace2'
                }
            ]
        }
        xml = etree.Element('root')
        
        resp_xml, resp_data = filters.listmetadataformats((xml, data))

        xml_str = '<root>'
        xml_str += '<ListMetadataFormats>'
        xml_str += '<metadataFormat>'
        xml_str += '<metadataPrefix>prefix</metadataPrefix>'
        xml_str += '<schema>schema</schema>'
        xml_str += '<metadataNamespace>namespace</metadataNamespace>'
        xml_str += '</metadataFormat>'
        xml_str += '<metadataFormat>'
        xml_str += '<metadataPrefix>prefix2</metadataPrefix>'
        xml_str += '<schema>schema2</schema>'
        xml_str += '<metadataNamespace>namespace2</metadataNamespace>'
        xml_str += '</metadataFormat>'
        xml_str += '</ListMetadataFormats>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(resp_xml), xml_str.encode('utf-8'))


class TestListIdentifiersPipe(unittest.TestCase):

    @unittest.skip('refatorar para eliminar o uso de threadlocals')
    def test_list_identifiers_add_one_header_for_each_identifier(self):
        data = {
            'verb': 'ListIdentifiers',
            'baseURL': 'http://books.scielo.org/oai/',
            'books': [
                {
                    'identifier': 'xpto',
                    'datestamp': datetime(2014, 2, 12, 10, 55, 0),
                    'publisher': 'Teste OAI-PMH'
                }, {
                    'identifier': 'xvzp',
                    'datestamp': datetime(2014, 1, 27, 10, 55, 0),
                    'publisher': 'OAI-PMH SciELO'
                }
            ]
        }
        root = etree.Element('root')

        xml, data = filters.listidentifiers((root, data))

        xml_str = '<root>'
        xml_str += '<ListIdentifiers>'
        xml_str += '<header>'
        xml_str += '<identifier>xpto</identifier>'
        xml_str += '<datestamp>2014-02-12</datestamp>'
        xml_str += '<setSpec>teste-oai-pmh</setSpec>'
        xml_str += '</header>'
        xml_str += '<header>'
        xml_str += '<identifier>xvzp</identifier>'
        xml_str += '<datestamp>2014-01-27</datestamp>'
        xml_str += '<setSpec>oai-pmh-scielo</setSpec>'
        xml_str += '</header>'
        xml_str += '</ListIdentifiers>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))

    def test_header_with_three_subelements(self):
        data = {
                'resources': [
                    {
                        'ridentifier': 'xpto',
                        'datestamp': datetime(2014, 2, 12, 10, 55, 0),
                        'setspec': ['cs', 'math']
                    },
                ]
        }
        root = etree.Element('root')
        xml, data = filters.listidentifiers((root, data))

        xml_str = '<root>'
        xml_str += '<ListIdentifiers>'
        xml_str += '<header>'
        xml_str += '<identifier>xpto</identifier>'
        xml_str += '<datestamp>2014-02-12</datestamp>'
        xml_str += '<setSpec>cs</setSpec>'
        xml_str += '<setSpec>math</setSpec>'
        xml_str += '</header>'
        xml_str += '</ListIdentifiers>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))

    def test_deleted_record(self):
        data = {
                'resources': [
                    {
                        'ridentifier': 'xpto',
                        'datestamp': datetime(2014, 2, 12, 10, 55, 0),
                        'setspec': ['cs', 'math'],
                        'deleted': True,
                    }
                ]
        }
        root = etree.Element('root')
        xml, data = filters.listidentifiers((root, data))

        self.assertEqual(xml.xpath('/root/ListIdentifiers/header/@status')[0], 'deleted')

    def test_deleted_markers_ignore_str_values(self):
        for val in ['True', 'False']:
            data = {
                    'resources': [
                        {
                            'ridentifier': 'xpto',
                            'datestamp': datetime(2014, 2, 12, 10, 55, 0),
                            'setspec': ['cs', 'math'],
                            'deleted': val,
                        }
                    ]
            }
            root = etree.Element('root')
            xml, data = filters.listidentifiers((root, data))

            self.assertEqual(xml.xpath('/root/ListIdentifiers/header/@status'), [])

    def test_deleted_markers_ignore_int_values(self):
        for val in [0, 1]:
            data = {
                    'resources': [
                        {
                            'ridentifier': 'xpto',
                            'datestamp': datetime(2014, 2, 12, 10, 55, 0),
                            'setspec': ['cs', 'math'],
                            'deleted': val,
                        }
                    ]
            }
            root = etree.Element('root')
            xml, data = filters.listidentifiers((root, data))

            self.assertEqual(xml.xpath('/root/ListIdentifiers/header/@status'), [])


class TestSetPipe(unittest.TestCase):

    def test_set_pipe_add_set_with_two_subelements(self):
        data = 'Editora UNESP'

        pipe = filters.SetPipe()
        xml = pipe.transform(data)

        xml_str = '<set>'
        xml_str += '<setSpec>editora-unesp</setSpec>'
        xml_str += '<setName>Editora UNESP</setName>'
        xml_str += '</set>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))


class TestListSetsPipe(unittest.TestCase):

    @unittest.skip('refatorar para eliminar o uso de threadlocals')
    def test_list_sets_add_one_set_for_each_publisher(self):
        data = {
            'verb': 'ListIdentifiers',
            'baseURL': 'http://books.scielo.org/oai/',
            'books': ['Teste OAI-PMH', 'OAI-PMH SciELO']
        }
        root = etree.Element('root')

        pipe = filters.ListSetsPipe()
        xml, data = pipe.transform((root, data))

        xml_str = '<root>'
        xml_str += '<ListSets>'
        xml_str += '<set>'
        xml_str += '<setSpec>teste-oai-pmh</setSpec>'
        xml_str += '<setName>Teste OAI-PMH</setName>'
        xml_str += '</set>'
        xml_str += '<set>'
        xml_str += '<setSpec>oai-pmh-scielo</setSpec>'
        xml_str += '<setName>OAI-PMH SciELO</setName>'
        xml_str += '</set>'
        xml_str += '</ListSets>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))


class TestRecordPipe(unittest.TestCase):

    @unittest.skip('melhorar a estratégia de comparação')
    def test_record_pipe_add_record_node(self):
        data = {
            'datestamp': datetime(2014, 2, 19, 13, 5, 0),
            'title': 'title',
            'creators': {
                'collaborator': [['collaborator', None]],
                'organizer': [['organizer', None]]
            },
            'description': 'description',
            'publisher': 'publisher',
            'date': '2014',
            'formats': ['pdf', 'epub'],
            'identifier': 'identifier',
            'language': 'pt'
        }

        xml = filters.record(data)

        xml_str = '<record>'
        xml_str += '<header>'
        xml_str += '<identifier>identifier</identifier>'
        xml_str += '<datestamp>2014-02-19</datestamp>'
        xml_str += '<setSpec>publisher</setSpec>'
        xml_str += '</header>'
        xml_str += '<metadata>'
        xml_str += '<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"'
        xml_str += ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        xml_str += ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        xml_str += ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/'
        xml_str += ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
        xml_str += '<dc:title>title</dc:title>'
        xml_str += '<dc:creator>organizer</dc:creator>'
        xml_str += '<dc:contributor>collaborator</dc:contributor>'
        xml_str += '<dc:description>description</dc:description>'
        xml_str += '<dc:publisher>publisher</dc:publisher>'
        xml_str += '<dc:date>2014</dc:date>'
        xml_str += '<dc:type>book</dc:type>'
        xml_str += '<dc:format>pdf</dc:format>'
        xml_str += '<dc:format>epub</dc:format>'
        xml_str += '<dc:identifier>http://books.scielo.org/id/identifier</dc:identifier>'
        xml_str += '<dc:language>pt</dc:language>'
        xml_str += '</oai_dc:dc>'
        xml_str += '</metadata>'
        xml_str += '</record>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))


class GetRecordTests(unittest.TestCase):

    @unittest.skip('refatorar para eliminar o uso de threadlocals')
    def test_get_record_pipe_add_get_record(self):
        data = {
            'verb': 'GetRecord',
            'baseURL': 'http://books.scielo.org/oai/',
            'resources': [{
                'datestamp': datetime(2014, 2, 19, 13, 5, 0),
                'title': 'title',
                'creators': {
                    'collaborator': [['collaborator', None]],
                    'organizer': [['organizer', None]]
                },
                'description': 'description',
                'publisher': 'publisher',
                'date': '2014',
                'formats': ['pdf', 'epub'],
                'identifier': 'identifier',
                'language': 'pt'
            }]
        }

        root = etree.Element('root')
        xml, data = filters.record((root, data))

        xml_str = '<root>'
        xml_str += '<GetRecord>'
        xml_str += '<record>'
        xml_str += '<header>'
        xml_str += '<identifier>identifier</identifier>'
        xml_str += '<datestamp>2014-02-19</datestamp>'
        xml_str += '<setSpec>publisher</setSpec>'
        xml_str += '</header>'
        xml_str += '<metadata>'
        xml_str += '<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"'
        xml_str += ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        xml_str += ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        xml_str += ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/'
        xml_str += ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
        xml_str += '<dc:title>title</dc:title>'
        xml_str += '<dc:creator>organizer</dc:creator>'
        xml_str += '<dc:contributor>collaborator</dc:contributor>'
        xml_str += '<dc:description>description</dc:description>'
        xml_str += '<dc:publisher>publisher</dc:publisher>'
        xml_str += '<dc:date>2014</dc:date>'
        xml_str += '<dc:type>book</dc:type>'
        xml_str += '<dc:format>pdf</dc:format>'
        xml_str += '<dc:format>epub</dc:format>'
        xml_str += '<dc:identifier>http://books.scielo.org/id/identifier</dc:identifier>'
        xml_str += '<dc:language>pt</dc:language>'
        xml_str += '</oai_dc:dc>'
        xml_str += '</metadata>'
        xml_str += '</record>'
        xml_str += '</GetRecord>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))


class ListRecordsTests(unittest.TestCase):

    @unittest.skip('refatorar para eliminar o uso de threadlocals')
    def test_list_records_pipe_add_many_records_node(self):
        data = {
            'verb': 'ListRecords',
            'baseURL': 'http://books.scielo.org/oai/',
            'books': [{
                'datestamp': datetime(2014, 2, 19, 13, 5, 0),
                'title': 'title',
                'creators': {
                    'collaborator': [['collaborator', None]],
                    'organizer': [['organizer', None]]
                },
                'description': 'description',
                'publisher': 'publisher',
                'date': '2014',
                'formats': ['pdf', 'epub'],
                'identifier': 'identifier',
                'language': 'pt'
            }]
        }

        root = etree.Element('root')
        xml, data = filters.listrecords((root, data))

        xml_str = '<root>'
        xml_str += '<ListRecords>'
        xml_str += '<record>'
        xml_str += '<header>'
        xml_str += '<identifier>identifier</identifier>'
        xml_str += '<datestamp>2014-02-19</datestamp>'
        xml_str += '<setSpec>publisher</setSpec>'
        xml_str += '</header>'
        xml_str += '<metadata>'
        xml_str += '<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"'
        xml_str += ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        xml_str += ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        xml_str += ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/'
        xml_str += ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
        xml_str += '<dc:title>title</dc:title>'
        xml_str += '<dc:creator>organizer</dc:creator>'
        xml_str += '<dc:contributor>collaborator</dc:contributor>'
        xml_str += '<dc:description>description</dc:description>'
        xml_str += '<dc:publisher>publisher</dc:publisher>'
        xml_str += '<dc:date>2014</dc:date>'
        xml_str += '<dc:type>book</dc:type>'
        xml_str += '<dc:format>pdf</dc:format>'
        xml_str += '<dc:format>epub</dc:format>'
        xml_str += '<dc:identifier>http://books.scielo.org/id/identifier</dc:identifier>'
        xml_str += '<dc:language>pt</dc:language>'
        xml_str += '</oai_dc:dc>'
        xml_str += '</metadata>'
        xml_str += '</record>'
        xml_str += '</ListRecords>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))


@unittest.skip('refatorar para eliminar o uso de threadlocals')
class TestResumptionTokenPipe(unittest.TestCase):
    
    @patch.object(Registry, 'settings')
    def test_resumption_token_add_next_token_if_not_finished(self, mock_settings):
        mock_settings.return_value = {'items_per_page': '2'}
        data = {
            'books': [{}, {}],
            'request': {}
        }
        root = etree.Element('root')

        pipe = filters.ResumptionTokenPipe()
        xml, data = pipe.transform((root, data))

        xml_str = '<root>'
        xml_str += '<resumptionToken>1</resumptionToken>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))

    @patch.object(Registry, 'settings')
    def test_resumption_token_empty_if_finished(self, mock_settings):
        mock_settings.return_value = {'items_per_page': '2'}
        data = {
            'books': [{}, {}],
            'request': {'resumptionToken': '1'}
        }
        root = etree.Element('root')

        pipe = filters.ResumptionTokenPipe()
        xml, data = pipe.transform((root, data))

        xml_str = '<root>'
        xml_str += '<resumptionToken/>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))
