import unittest
from unittest.mock import patch
from datetime import datetime

from oaipmh import assemblers


class MakeIdentifyTests(unittest.TestCase):
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

