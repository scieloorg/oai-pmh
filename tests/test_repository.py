import re
import unittest
from collections import namedtuple
import urllib.parse

from .fixtures import factories
from oaipmh.formatters import (
        oai_dc,
        oai_dc_openaire,
        )
from oaipmh import (
        repository,
        datastores,
        sets,
        entities,
        )


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


class BaseRepositoryTests:
    def setUp(self):
        meta = factories.get_sample_repositorymeta()
        self.ds = datastores.InMemory()
        self.setsreg = sets.InMemory()
        datestamp_validator = lambda x: re.fullmatch(
                r'^(\d{4})-(\d{2})-(\d{2})$', x)
        resultpage_factory = repository.ResultPageFactory(ds=self.ds,
                setsreg=self.setsreg, listslen=10,
                granularity_validator=datestamp_validator,
                chunk_size=3,
                earliest_datestamp=meta.earliestDatestamp)
        self.repository = repository.Repository(meta, self.ds,
                datestamp_validator, resultpage_factory=resultpage_factory)
        self._post_setup()

    def _post_setup(self):
        return None

class RepositoryTests(BaseRepositoryTests, unittest.TestCase):
    def test_handling_req_with_illegal_args(self):
        req = 'verb=Identify&illegalarg=foo'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)

    def test_handling_req_with_repeated_args(self):
        req = 'verb=Identify&verb=Identify'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)

    def test_handling_req_to_invalid_verb(self):
        req = 'verb=InvalidVerb'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badVerb"'.encode('utf-8') in result)
        #verbo ilegal não deve ser valor de request/@verb
        self.assertTrue('<request>'.encode('utf-8') in result)

    def test_handling_invalid_utcdatetimetypes(self):
        req = 'verb=ListRecords&from=foo'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)
        #verbo ilegal não deve ser valor de request/@verb
        self.assertTrue('<request verb="ListRecords">'.encode('utf-8') in result)


class ListIdentifiersTests(BaseRepositoryTests, unittest.TestCase):
    metadata_formats = [
            (entities.MetadataFormat(
                metadataPrefix='oai_dc',
                schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                metadataNamespace='http://www.openarchives.org/OAI/2.0/oai_dc/'),
             oai_dc.make_metadata,
             lambda x: x),
            (entities.MetadataFormat(
                metadataPrefix='oai_dc_openaire',
                schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                metadataNamespace='http://www.openarchives.org/OAI/2.0/oai_dc/'),
             oai_dc_openaire.make_metadata,
             oai_dc_openaire.augment_metadata),
            ]

    def _post_setup(self):
        for metadata, formatter, augmenter in self.metadata_formats:
            self.repository.add_metadataformat(metadata, formatter, augmenter)

    def test_wrong_granularity_in_from_arg(self):
        req = 'verb=ListIdentifiers&from=2002-01-01T00:00:00Z'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)
        
    def test_wrong_granularity_in_until_arg(self):
        req = 'verb=ListIdentifiers&until=2002-01-01T00:00:00Z'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)
        
    def test_when_from_and_until_granularities_are_different(self):
        req = 'verb=ListIdentifiers&from=2000-01-01&until=2002-01-01T00:00:00Z'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)

    def test_when_from_is_greater_than_until(self):
        req = 'verb=ListIdentifiers&from=2003-01-01&until=2002-01-01'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)

    def test_empty_list_returns_norecordsmatch_error(self):
        req = 'verb=ListIdentifiers&metadataPrefix=oai_dc'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="noRecordsMatch"'.encode('utf-8') in result)


class ListRecordsTests(BaseRepositoryTests, unittest.TestCase):
    metadata_formats = [
            (entities.MetadataFormat(
                metadataPrefix='oai_dc',
                schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                metadataNamespace='http://www.openarchives.org/OAI/2.0/oai_dc/'),
             oai_dc.make_metadata,
             lambda x: x),
            (entities.MetadataFormat(
                metadataPrefix='oai_dc_openaire',
                schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                metadataNamespace='http://www.openarchives.org/OAI/2.0/oai_dc/'),
             oai_dc_openaire.make_metadata,
             oai_dc_openaire.augment_metadata),
            ]

    def _post_setup(self):
        for metadata, formatter, augmenter in self.metadata_formats:
            self.repository.add_metadataformat(metadata, formatter, augmenter)

    def test_wrong_granularity_in_from_arg(self):
        req = 'verb=ListRecords&from=2002-01-01T00:00:00Z'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)
        
    def test_wrong_granularity_in_until_arg(self):
        req = 'verb=ListRecords&until=2002-01-01T00:00:00Z'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)
        
    def test_when_from_and_until_granularities_are_different(self):
        req = 'verb=ListRecords&from=2000-01-01&until=2002-01-01T00:00:00Z'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)

    def test_when_from_is_greater_than_until(self):
        req = 'verb=ListRecords&from=2003-01-01&until=2002-01-01'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="badArgument"'.encode('utf-8') in result)

    def test_empty_list_returns_norecordsmatch_error(self):
        req = 'verb=ListRecords&metadataPrefix=oai_dc'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="noRecordsMatch"'.encode('utf-8') in result)


class ListMetadataFormatsTests(BaseRepositoryTests, unittest.TestCase):
    def test_arg_identifier_is_allowed(self):
        resource = factories.get_sample_resource()
        self.ds.add(resource)

        req = 'verb=ListMetadataFormats&identifier=%s' % resource.ridentifier
        result = self.repository.handle_request(req)
        self.assertFalse('<error code="badArgument"'.encode('utf-8') in result)

    def test_unknown_identifier_returns_iddoesnotexist_error(self):
        req = 'verb=ListMetadataFormats&identifier=unknownid'
        result = self.repository.handle_request(req)
        self.assertTrue('<error code="idDoesNotExist"'.encode('utf-8') in result)


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


class are_equalTests(unittest.TestCase):
    def test_equal_seqs(self):
        self.assertTrue(repository.are_equal(['foo', 'bar', 'blah'],
            ['foo', 'bar', 'blah']))

    def test_equal_but_unsorted_seqs(self):
        self.assertTrue(repository.are_equal(['blah', 'bar', 'foo'],
            ['foo', 'bar', 'blah']))

    def test_unequal_seqs(self):
        self.assertFalse(repository.are_equal(['foo', 'bar', 'blah'],
            ['zap', 'blah', 'foo']))

    def test_seqs_with_different_lengths(self):
        self.assertFalse(repository.are_equal(['foo', 'bar', 'blah'],
            ['zap', 'blah']))


class check_listrecords_argsTests(unittest.TestCase):
    def test_verb_is_missing(self):
        self.assertFalse(repository.check_listrecords_args([]))

    def test_verb_nand_resumptiontoken_and_metadataprefix(self):
        self.assertTrue(repository.check_listrecords_args(
            ['verb', 'metadataPrefix']))

    def test_verb_nand_resumptiontoken_nand_metadataprefix(self):
        self.assertFalse(repository.check_listrecords_args(['verb']))

    def test_verb_and_resumptiontoken_and_anythingelse_case1(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'until', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case2(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'until', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case3(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'until', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case4(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'until']))

    def test_verb_and_resumptiontoken_and_anythingelse_case5(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case6(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case7(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case8(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'from']))

    def test_verb_and_resumptiontoken_and_anythingelse_case9(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'until', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case10(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'until', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case11(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'until', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case12(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'until']))

    def test_verb_and_resumptiontoken_and_anythingelse_case13(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case14(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case15(self):
        self.assertFalse(repository.check_listrecords_args(
            ['verb', 'resumptionToken', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_nand_anyfilter(self):
        self.assertTrue(repository.check_listrecords_args(
            ['verb', 'resumptionToken']))


class check_listmetadataformats_argsTests(unittest.TestCase):
    def test_verb_is_missing(self):
        self.assertFalse(repository.check_listmetadataformats_args([]))

    def test_verb_nand_resumptiontoken_and_metadataprefix(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'metadataPrefix']))

    def test_verb_nand_resumptiontoken_nand_metadataprefix(self):
        self.assertTrue(repository.check_listmetadataformats_args(['verb']))

    def test_verb_and_resumptiontoken_and_anythingelse_case1(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'until', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case2(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'until', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case3(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'until', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case4(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'until']))

    def test_verb_and_resumptiontoken_and_anythingelse_case5(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case6(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case7(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case8(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'from']))

    def test_verb_and_resumptiontoken_and_anythingelse_case9(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'until', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case10(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'until', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case11(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'until', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case12(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'until']))

    def test_verb_and_resumptiontoken_and_anythingelse_case13(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'set', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_and_anythingelse_case14(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case15(self):
        self.assertFalse(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken', 'metadataPrefix']))

    def test_verb_and_resumptiontoken_nand_anyfilter(self):
        self.assertTrue(repository.check_listmetadataformats_args(
            ['verb', 'resumptionToken']))


class check_listsets_argsTests(unittest.TestCase):
    def test_verb_is_missing(self):
        self.assertFalse(repository.check_listsets_args([]))

    def test_verb_nand_resumptiontoken_and_metadataprefix(self):
        self.assertFalse(repository.check_listsets_args(
            ['verb', 'metadataPrefix']))

    def test_verb_nand_resumptiontoken_nand_metadataprefix(self):
        self.assertTrue(repository.check_listsets_args(['verb']))

    def test_verb_and_resumptiontoken_and_anythingelse_case1(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'from', 'until', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case2(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'from', 'until']))

    def test_verb_and_resumptiontoken_and_anythingelse_case3(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'from', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case4(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'from']))

    def test_verb_and_resumptiontoken_and_anythingelse_case5(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'until', 'set']))

    def test_verb_and_resumptiontoken_and_anythingelse_case6(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'until']))

    def test_verb_and_resumptiontoken_and_anythingelse_case7(self):
        self.assertFalse(repository.check_listsets_args(
        ['verb', 'resumptionToken', 'set']))

