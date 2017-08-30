import os
import unittest
from datetime import datetime

from oaipmh import articlemeta, entities


FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        'fixtures')


def get_article_fixture():
    import json
    from xylose.scielodocument import Article

    raw_article_path = os.path.join(FIXTURES_DIR, 'article_type3.json')
    with open(raw_article_path) as f:
        raw_article = json.load(f)
    article = Article(raw_article)
    return article


class ResourceFacadeTests(unittest.TestCase):
    def setUp(self):
        self.article = get_article_fixture()
        self.resource_fac = articlemeta.ArticleResourceFacade(self.article)

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
        self.assertIsInstance(resource, entities.Resource)


class ArticleMetaTests(unittest.TestCase):
    def test_get_known_resource_returns_namedtuple_resource(self):
        class ClientStub:
            def document(self, ridentifier):
                return get_article_fixture()

        am = articlemeta.ArticleMeta(ClientStub())
        self.assertIsInstance(am.get('validID'), entities.Resource)

