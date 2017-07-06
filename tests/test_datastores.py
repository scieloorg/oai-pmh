import os
import unittest
from datetime import datetime

from .fixtures import factories
from oaipmh import datastores


FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        'fixtures')


class InMemoryTests(unittest.TestCase):
    def setUp(self):
        self.store = datastores.InMemory()

    def test_new_resource(self):
        resource = factories.get_sample_resource()
        self.store.add(resource)
        self.assertEqual(self.store.get(resource.ridentifier), resource)

    def test_factories_can_be_overrided(self):
        resource = factories.get_sample_resource()
        self.store.add(resource)

        resource2 = factories.get_sample_resource(title=[('pt', 'New title')])
        self.store.add(resource2)

        self.assertEqual(self.store.get(resource.ridentifier), resource2)
        
    def test_missing_resource(self):
        self.assertRaises(datastores.DoesNotExistError, 
                lambda: self.store.get('missing-ridentifier'))

    def test_list_all(self):
        sample_factories = [factories.get_sample_resource(ridentifier='rid-'+str(i))
                            for i in range(100)]

        for resource in sample_factories:
            self.store.add(resource)

        retrieved_factories = list(self.store.list())
        self.assertEqual(sample_factories, retrieved_factories)

    def test_list_single_set(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_factories = [factories.get_sample_resource(**d)
                            for d in data]

        for resource in sample_factories:
            self.store.add(resource)

        set1_factories = list(self.store.list(sets=['set1']))
        self.assertEqual(len(set1_factories), 100)

    def test_list_two_sets(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_factories = [factories.get_sample_resource(**d)
                            for d in data]

        for resource in sample_factories:
            self.store.add(resource)

        set1_factories = list(self.store.list(sets=['set1', 'set2']))
        self.assertEqual(len(set1_factories), 200)

    def test_counted_list(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_factories = [factories.get_sample_resource(**d)
                            for d in data]

        for resource in sample_factories:
            self.store.add(resource)

        set1_factories = list(self.store.list(sets=['set1', 'set2'], count=10))
        self.assertEqual(len(set1_factories), 10)

    def test_offset_list(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_factories = [factories.get_sample_resource(**d)
                            for d in data]

        for resource in sample_factories:
            self.store.add(resource)

        set1_factories = list(self.store.list(sets=['set1', 'set2'],
            offset=0, count=10))
        set1_factories += list(self.store.list(sets=['set1', 'set2'],
            offset=10, count=10))
        
        set2_factories = list(self.store.list(sets=['set1', 'set2'],
            offset=0, count=20))
        
        self.assertEqual(set1_factories, set2_factories)

    def test_from_datestamp(self):
        data = [{'ridentifier': 'rid'+str(i), 'datestamp': '2017-06-0%s' % i} 
                for i in range(10)]

        sample_factories = [factories.get_sample_resource(**d)
                            for d in data]

        for resource in sample_factories:
            self.store.add(resource)

        set_factories = list(self.store.list(_from='2017-06-05'))
        self.assertEqual(len(set_factories), 5)

    def test_until_datestamp(self):
        data = [{'ridentifier': 'rid'+str(i), 'datestamp': '2017-06-0%s' % i} 
                for i in range(10)]

        sample_factories = [factories.get_sample_resource(**d)
                            for d in data]

        for resource in sample_factories:
            self.store.add(resource)

        set_factories = list(self.store.list(until='2017-06-05'))
        self.assertEqual(len(set_factories), 5)


class DatestampToTupleTests(unittest.TestCase):
    def test_best_case_conversion(self):
        self.assertEqual(datastores.datestamp_to_tuple('2017-06-19'),
                (2017, 6, 19))

    def test_non_numerical_strings_raise_typeerror(self):
        self.assertRaises(ValueError,
                lambda: datastores.datestamp_to_tuple('2017-06-X'))


def get_article_fixture():
    import json
    from xylose.scielodocument import Article

    raw_article_path = os.path.join(FIXTURES_DIR, 'article_type3.json')
    raw_article = json.load(open(raw_article_path))
    article = Article(raw_article)
    return article


class ResourceFacadeTests(unittest.TestCase):
    def setUp(self):
        self.article = get_article_fixture()
        self.resource_fac = datastores.ArticleResourceFacade(self.article)

    def test_ridentifier(self):
        self.assertEqual('S2179-975X2011000300002',
                self.resource_fac.ridentifier())

    def test_datestamp(self):
        self.assertEqual(datetime(2012, 4, 19),
                self.resource_fac.datestamp())

    def test_setspec(self):
        self.assertEqual([],
                self.resource_fac.setspec())

    def test_original_title_comes_first(self):
        titles = self.resource_fac.title()
        lang, title = titles[0]
        self.assertEqual(lang, 'en')
        self.assertTrue(title.startswith('First adult record of Misgurnus'))

    def test_translated_titles_are_there(self):
        titles = self.resource_fac.title()
        langs = [lang for lang, _ in titles]
        self.assertTrue('pt' in langs)
        
    def test_first_author_comes_first(self):
        creators = self.resource_fac.creator()
        self.assertEqual(creators[0],
                'Gomes, Caio Isola Dallevo do Amaral')

    def test_subject(self):
        expected = [('en', 'Oriental weatherfish'),
                    ('en', 'exotic species'),
                    ('en', 'sexual maturity'),
                    ('en', 'diet overlap'),
                    ('en', 'São Paulo State'),
                    ('pt', 'Dojo'),
                    ('pt', 'espécies exóticas'),
                    ('pt', 'maturidade sexual'),
                    ('pt', 'sobreposição de dieta'),
                    ('pt', 'Estado de São Paulo')]
        self.assertEqual(expected, self.resource_fac.subject())

    def test_description(self):
        description = self.resource_fac.description()
        descr_dict = dict(description)
        langs = list(descr_dict.keys())

        self.assertEqual(sorted(langs), sorted(['pt', 'en']))
        self.assertTrue(descr_dict['pt'].startswith('OBJETIVO'))
        self.assertTrue(descr_dict['en'].startswith('AIM'))

    def test_date_uses_the_publication_date(self):
        date = self.resource_fac.date()
        self.assertEqual(date, [datetime(2011, 9, 1)])

    def test_type_uses_the_document_type(self):
        typ = self.resource_fac.type()
        self.assertEqual(typ, ['research-article'])

    def test_identifier_returns_an_url_to_html(self):
        identifier = self.resource_fac.identifier()
        self.assertTrue(identifier,
                ['http://www.scielo.br/scielo.php?script=sci_arttext&pid=S2179-975X2011000300002&lng=en&tlng=en'])

    def test_language_returns_the_original_language(self):
        lang = self.resource_fac.language()
        self.assertEqual(lang, ['en'])

    def test_rights_returns_the_license_url(self):
        rights = self.resource_fac.rights()
        self.assertEqual(rights, 
                ['http://creativecommons.org/licenses/by-nc/4.0/'])

    def test_resource_instantiation(self):
        resource = self.resource_fac.to_resource()
        self.assertIsInstance(resource, datastores.Resource)


class ArticleMetaTests(unittest.TestCase):
    def test_get_known_resource_returns_namedtuple_resource(self):
        class ClientStub:
            def document(self, ridentifier):
                return get_article_fixture()

        am = datastores.ArticleMeta(ClientStub())
        self.assertIsInstance(am.get('validID'), datastores.Resource)

