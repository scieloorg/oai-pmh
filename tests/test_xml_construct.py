import unittest
from unittest.mock import patch
from datetime import datetime

from lxml import etree

from oaipmh import serializers
from oaipmh.formatters import oai_dc


class RootTests(unittest.TestCase):
    def test_returns_pair_of_values(self):
        data = {}
        resp = serializers.root(data)

        self.assertEqual(len(resp), 2)

    def test_root_element_tagname(self):
        data = {}
        resp_xml, _ = serializers.root(data)
        
        self.assertEqual(resp_xml.tag, 'OAI-PMH')

    def test_root_element_attributes(self):
        data = {}
        resp_xml, _ = serializers.root(data)
        
        expected_attrs = {
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd',
                }

        for name, value in expected_attrs.items():
            self.assertEqual(resp_xml.attrib[name], value)


class ResponseDateTests(unittest.TestCase):
    def test_responseDate_element_is_added(self):
        xml = etree.Element('root')
        
        resp_xml, _ = serializers.responsedate((xml, {}))
        self.assertEqual(len(resp_xml), 1)
        self.assertEqual(resp_xml[0].tag, 'responseDate')

    @patch('oaipmh.serializers.datetime')
    def test_responseDate_is_UTC(self, mock_utc):
        mock_utc.utcnow.return_value = datetime(2014, 2, 6, 15, 17, 0)
        xml = etree.Element('root')
        
        resp_xml, _ = serializers.responsedate((xml, {}))
        self.assertEqual(resp_xml[0].text, '2014-02-06T15:17:00Z')


class RequestTests(unittest.TestCase):
    def test_request_add_verb_and_base_url(self):
        data = {
            'repository': {'baseURL': 'http://books.scielo.org/oai/'},
            'request': {'verb': 'Identifier'}
        }
        xml = etree.Element('root')
        
        resp_xml, _ = serializers.request((xml, data))

        xml_str = '<root><request verb="Identifier">http://books.scielo.org/oai/</request></root>'

        self.assertEqual(etree.tostring(resp_xml), xml_str.encode('utf-8'))

    def test_arbitrary_items_are_represented_as_attrs(self):
        data = {
            'repository': {'baseURL': 'http://books.scielo.org/oai/'},
            'request': {'verb': 'Identifier', 'foo': 'bar'}
        }
        xml = etree.Element('root')
        
        resp_xml, _ = serializers.request((xml, data))
        self.assertEqual(resp_xml[0].attrib['foo'], 'bar') 


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

        resp_xml, _ = serializers.identify((xml, data))

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
        
        resp_xml = serializers.tobytes((xml, data))

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
        
        resp_xml, resp_data = serializers.listmetadataformats((xml, data))

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


class ListIdentifiersTests(unittest.TestCase):
    def test_one_not_deleted_record(self):
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
        xml, data = serializers.listidentifiers((root, data))

        xml_str = '<root>'
        xml_str += '<ListIdentifiers>'
        xml_str += '<header>'
        xml_str += '<identifier>xpto</identifier>'
        xml_str += '<datestamp>2014-02-12</datestamp>'
        xml_str += '<setSpec>cs</setSpec>'
        xml_str += '<setSpec>math</setSpec>'
        xml_str += '</header>'
        xml_str += '<resumptionToken></resumptionToken>'
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
        xml, data = serializers.listidentifiers((root, data))

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
            xml, data = serializers.listidentifiers((root, data))

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
            xml, data = serializers.listidentifiers((root, data))

            self.assertEqual(xml.xpath('/root/ListIdentifiers/header/@status'), [])


class ListSetsTests(unittest.TestCase):

    def test_list_sets_add_one_set_for_each_publisher(self):
        data = {
                'request': {'verb': 'ListIdentifiers'},
                'repository': {'baseURL': 'http://books.scielo.org/oai/'},
                'sets': [
                    {'setSpec': 'foo', 'setName': 'bar'},
                ]
        }
        root = etree.Element('root')

        xml, data = serializers.listsets((root, data))

        xml_str = '<root>'
        xml_str += '<ListSets>'
        xml_str += '<set>'
        xml_str += '<setSpec>foo</setSpec>'
        xml_str += '<setName>bar</setName>'
        xml_str += '</set>'
        xml_str += '<resumptionToken></resumptionToken>'
        xml_str += '</ListSets>'
        xml_str += '</root>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))


class RecordMakerTests(unittest.TestCase):

    def test_serialize_resource_into_record(self):
        data = {
                'ridentifier': 'S0001-37652000000200015',
                'datestamp': datetime(2000, 8, 7, 0, 0),
                'setspec': ['0001-3765'],
                'title': [('en', 'Hydrogeology of Brasília (DF) Sobradinho river basin')],
                'creator': ['Zoby, José Luiz G.', 'Duarte, Uriel'],
                'subject': [],
                'description': [('en', None)],
                'publisher': ['Academia Brasileira de Ciências'],
                'contributor': [],
                'date': [datetime(2000, 6, 1, 0, 0)],
                'type': ['abstract'],
                'format': ['text/html'],
                'identifier': ['http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0001-37652000000200015&lng=en&tlng=en'],
                'source': ['An. Acad. Bras. Ciênc. vol.72 n.2 Rio de Janeiro June 2000'],
                'language': ['en'],
                'relation': [],
                'rights': ['http://creativecommons.org/licenses/by-nc/4.0/']
                }

        xml = serializers.make_record(data, oai_dc.make_metadata)

        xml_str = '<record><header><identifier>S0001-37652000000200015</identifier><datestamp>2000-08-07</datestamp><setSpec>0001-3765</setSpec></header><metadata><oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"><dc:title>Hydrogeology of Bras&#237;lia (DF) Sobradinho river basin</dc:title><dc:creator>Zoby, Jos&#233; Luiz G.</dc:creator><dc:creator>Duarte, Uriel</dc:creator><dc:description/><dc:publisher>Academia Brasileira de Ci&#234;ncias</dc:publisher><dc:date>2000-06-01</dc:date><dc:type>abstract</dc:type><dc:format>text/html</dc:format><dc:identifier>http://www.scielo.br/scielo.php?script=sci_arttext&amp;pid=S0001-37652000000200015&amp;lng=en&amp;tlng=en</dc:identifier><dc:language>en</dc:language></oai_dc:dc></metadata></record>'

        self.assertEqual(etree.tostring(xml), xml_str.encode('utf-8'))

