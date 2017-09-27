import os
import unittest
from datetime import datetime

from oaipmh import articlemeta, entities


class ArticleMetaStub:
    publisher_id = 'S2179-975X2011000300002'
    processing_date = '2012-04-19'

    def any_issn(self):
        return '2179-975X'

    def original_language(self):
        return 'en'

    def original_title(self):
        return 'First adult record of Misgurnus anguillicaudatus, Cantor 1842 from Ribeira de Iguape River Basin, Brazil'

    def translated_titles(self):
        return {'pt': 'Primeiro registro de um indivíduo adulto de Misgurnus anguillicaudatus, Cantor 1842 do rio Ribeira de Iguape, Brasil'}
    authors = [{'surname': 'Gomes', 'given_names': 'Caio Isola Dallevo do Amaral', 'role': 'ND', 'xref': ['A01']}, {'surname': 'Peressin', 'given_names': 'Alexandre', 'role': 'ND', 'xref': ['A02']}, {'surname': 'Cetra', 'given_names': 'Mauricio', 'role': 'ND', 'xref': ['A03']}, {'surname': 'Barrella', 'given_names': 'Walter', 'role': 'ND', 'xref': ['A04']}]

    def keywords(self):
        return {'en': ['Oriental weatherfish', 'exotic species', 'sexual maturity', 'diet overlap', 'São Paulo State'], 'pt': ['Dojo', 'espécies exóticas', 'maturidade sexual', 'sobreposição de dieta', 'Estado de São Paulo']}

    def original_abstract(self):
        return 'AIM: This work aimed to describe a first record of Misgurnus anguilicaudatus, Cantor 1842 in São Paulo state, as well as your potential impacts on native populations. METHODS: The specimen was caught by eletro-fishing device, in Itaguapeva river, Ribeira do Iguape river basin, Ibiuna (SP), Brazil. Later, it was fixed in 10% formalin and taken to laboratory for species identification, morphometric data evaluation, diet analysis and stage of gondal maturity. RESULTS: The individual was an adult female, without parasites and with gonads in maturity stage B, which indicates vascularized ovaries and presence of oocytes in vitellogenesis process. The dietary analysis showed that 95.3% of the stomach was occupied by insect larvae. CONCLUSIONS: The diet analysis may suggest food overlap and consequent competition for food with native species of the genera Trichomycterus e Characidium, which consume essentially the same items. Still, the great morphological similarity with native species, especially Siluriformes, could generate competition for shelters. Additionally, the stage of gonadal maturity and a recorded ability of the species on establish invasive populations in different environments raise concerns about the possibility of Misgurnus anguillicaudatus reproduction on the studied site.'

    def translated_abstracts(self):
        return {'pt': 'OBJETIVO: Este trabalho objetivou descrever o primeiro registro de Misgurnus anguillicaudatus, Cantor 1842 no estado de São Paulo, bem como seus potenciais impactos em populações nativas. MÉTODOS: O exemplar foi capturado com equipamento de pesca elétrica, no Rio Itaguapeva, bacia hidrográfica do Rio Ribeira de Iguape, no Município de Ibíuna (SP), Brasil. Posteriormente, foi fixado em formalina 10% e levado ao laboratório, para identificação da espécie, coleta de dados morfométricos, avaliação do estádio de maturidade gonadal (Vazzoler, 1996) e análise do conteúdo estomacal. RESULTADOS: O indivíduo capturado era uma fêmea adulta, sem parasitas e com gônadas em estádio de maturidade B, que indica ovários já vascularizados e presença de ovócitos em processo de vitelogênese. A análise da dieta revelou que 95,3% do estômago era ocupado por larvas de insetos. CONCLUSÕES: A composição da dieta pode sugerir sobreposição alimentar e conseqüente competição por alimento com espécies nativas dos gêneros Trichomycterus e Characidium, que consomem essencialmente os mesmo itens. Ainda, a grande semelhança morfológica com espécies nativas, principalmente Siluriformes, poderia gerar disputa por abrigos. Adicionalmente, o estádio de maturidade gonadal e a já registrada capacidade da espécie de estabelecer populações invasoras em diversos ambientes geram preocupações quanto à possibilidade de reprodução da espécie no local.'}

    @property
    def journal(self):
        class JournalStub:
            publisher_name = 'Editora Foo'
        return JournalStub()

    publication_date = '2012-02-16'
    document_type = 'research-article'
    def html_url(self):
        return 'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S2179-975X2011000300002&lng=en&tlng=en'

    def bibliographic_legends(self):
        return {'descriptive_format': 'RAE eletrônica, Volume: 4, Issue: 1, Published: JUN 2005'}

    permissions = {'text': 'This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License.', 'url': 'http://creativecommons.org/licenses/by-nc/4.0/', 'id': 'by-nc/4.0'}


class ResourceFacadeTests(unittest.TestCase):
    def setUp(self):
        self.article = ArticleMetaStub()
        self.resource_fac = articlemeta.ArticleResourceFacade(self.article)

    def test_ridentifier(self):
        self.assertEqual('S2179-975X2011000300002',
                self.resource_fac.ridentifier())

    def test_datestamp(self):
        self.assertEqual(datetime(2012, 4, 19),
                self.resource_fac.datestamp())

    def test_setspec(self):
        self.assertEqual(['2179-975X'],
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
        self.assertEqual(date, [datetime(2012, 2, 16)])

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
                return ArticleMetaStub()

        am = articlemeta.ArticleMeta(ClientStub())
        self.assertIsInstance(am.get('validID'), entities.Resource)


class VirtualOffsetTranslationTests(unittest.TestCase):
    def test_case_1(self):
        self.assertEqual(articlemeta.translate_virtual_offset(10, 0), 0)

    def test_case_2(self):
        self.assertEqual(articlemeta.translate_virtual_offset(10, 0), 0)

    def test_case_3(self):
        self.assertEqual(articlemeta.translate_virtual_offset(150, 0), 0)

    def test_case_4(self):
        self.assertEqual(articlemeta.translate_virtual_offset(150, 101), 0)

