import unittest
from datetime import datetime

from oaipmh.formatters import oai_dc_openaire


class FetchPubTypeFromVocabularyTests(unittest.TestCase):
    def test_research_article_returns_article(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('research-article'),
                'info:eu-repo/semantics/article')

    def test_article_commentary_returns_article(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('article-commentary'),
                'info:eu-repo/semantics/other')

    def test_book_review_returns_review(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('book-review'),
                'info:eu-repo/semantics/review')

    def test_brief_report_returns_report(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('brief-report'),
                'info:eu-repo/semantics/report')

    def test_case_report_returns_report(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('case-report'),
                'info:eu-repo/semantics/report')

    def test_correction_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('correction'),
                'info:eu-repo/semantics/other')

    def test_editorial_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('editorial'),
                'info:eu-repo/semantics/other')

    def test_in_brief_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('in-brief'),
                'info:eu-repo/semantics/other')

    def test_letter_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('letter'),
                'info:eu-repo/semantics/other')

    def test_other_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('other'),
                'info:eu-repo/semantics/other')

    def test_partial_retraction_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('partial-retraction'),
                'info:eu-repo/semantics/other')

    def test_rapid_communication_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('rapid-communication'),
                'info:eu-repo/semantics/other')

    def test_reply_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('reply'),
                'info:eu-repo/semantics/other')

    def test_retraction_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('retraction'),
                'info:eu-repo/semantics/other')

    def test_review_article_returns_article(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('review-article'),
                'info:eu-repo/semantics/article')

    def test_unknown_value_returns_other(self):
        self.assertEqual(oai_dc_openaire.fetch_pubtype_from_vocabulary('foo'),
                'info:eu-repo/semantics/other')


class MakeTitleTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'title': [('en', 'foo'), ('en', 'bar')]}

    def test_titles_are_multivalued(self):
        title_elements = oai_dc_openaire.make_title(self.resource)
        self.assertEqual(len(title_elements), 2)

    def test_titles_are_ordered(self):
        title_elements = oai_dc_openaire.make_title(self.resource)
        self.assertEqual(title_elements[0].text, 'foo')
        self.assertEqual(title_elements[1].text, 'bar')

    def test_titles_have_no_attrs(self):
        title_elements = oai_dc_openaire.make_title(self.resource)
        for element in title_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        title_elements = oai_dc_openaire.make_title(self.resource)
        for element in title_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}title')


class MakeCreatorTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'creator': ['foo', 'bar']}

    def test_creators_are_multivalued(self):
        creator_elements = oai_dc_openaire.make_creator(self.resource)
        self.assertEqual(len(creator_elements), 2)

    def test_creators_are_ordered(self):
        creator_elements = oai_dc_openaire.make_creator(self.resource)
        self.assertEqual(creator_elements[0].text, 'foo')
        self.assertEqual(creator_elements[1].text, 'bar')

    def test_creators_have_no_attrs(self):
        creator_elements = oai_dc_openaire.make_creator(self.resource)
        for element in creator_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        creator_elements = oai_dc_openaire.make_creator(self.resource)
        for element in creator_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}creator')


class MakeContributorTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'contributor': ['foo', 'bar']}

    def test_contributors_are_multivalued(self):
        contributor_elements = oai_dc_openaire.make_contributor(self.resource)
        self.assertEqual(len(contributor_elements), 2)

    def test_contributors_are_ordered(self):
        contributor_elements = oai_dc_openaire.make_contributor(self.resource)
        self.assertEqual(contributor_elements[0].text, 'foo')
        self.assertEqual(contributor_elements[1].text, 'bar')

    def test_contributors_have_no_attrs(self):
        contributor_elements = oai_dc_openaire.make_contributor(self.resource)
        for element in contributor_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        contributor_elements = oai_dc_openaire.make_contributor(self.resource)
        for element in contributor_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}contributor')


class MakeDescriptionTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'description': [('en', 'foo'), ('en', 'bar')]}
        
    def test_descriptions_are_multivalued(self):
        description_elements = oai_dc_openaire.make_description(self.resource)
        self.assertEqual(len(description_elements), 2)

    def test_contributors_are_ordered(self):
        description_elements = oai_dc_openaire.make_description(self.resource)
        self.assertEqual(description_elements[0].text, 'foo')
        self.assertEqual(description_elements[1].text, 'bar')

    def test_contributors_have_no_attrs(self):
        description_elements = oai_dc_openaire.make_description(self.resource)
        for element in description_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        description_elements = oai_dc_openaire.make_description(self.resource)
        for element in description_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}description')


class MakePublisherTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'publisher': ['foo', 'bar']}

    def test_publishers_are_multivalued(self):
        publisher_elements = oai_dc_openaire.make_publisher(self.resource)
        self.assertEqual(len(publisher_elements), 2)

    def test_publishers_are_ordered(self):
        publisher_elements = oai_dc_openaire.make_publisher(self.resource)
        self.assertEqual(publisher_elements[0].text, 'foo')
        self.assertEqual(publisher_elements[1].text, 'bar')

    def test_publishers_have_no_attrs(self):
        publisher_elements = oai_dc_openaire.make_publisher(self.resource)
        for element in publisher_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        publisher_elements = oai_dc_openaire.make_publisher(self.resource)
        for element in publisher_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}publisher')


class MakeDateTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'date': [datetime(2017, 6, 29), datetime(2016, 6, 1)]}

    def test_dates_are_multivalued(self):
        date_elements = oai_dc_openaire.make_date(self.resource)
        self.assertEqual(len(date_elements), 2)

    def test_dates_are_ordered(self):
        date_elements = oai_dc_openaire.make_date(self.resource)
        self.assertEqual(date_elements[0].text, '2017-06-29')
        self.assertEqual(date_elements[1].text, '2016-06-01')

    def test_publishers_have_no_attrs(self):
        date_elements = oai_dc_openaire.make_date(self.resource)
        for element in date_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        date_elements = oai_dc_openaire.make_date(self.resource)
        for element in date_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}date')


class MakeTypeTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'type': ['foo', 'bar']}

    def test_type_are_multivalued(self):
        type_elements = oai_dc_openaire.make_type(self.resource)
        self.assertEqual(len(type_elements), 2)

    def test_dates_are_ordered(self):
        type_elements = oai_dc_openaire.make_type(self.resource)
        self.assertEqual(type_elements[0].text, 'foo')
        self.assertEqual(type_elements[1].text, 'bar')

    def test_publishers_have_no_attrs(self):
        type_elements = oai_dc_openaire.make_type(self.resource)
        for element in type_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        type_elements = oai_dc_openaire.make_type(self.resource)
        for element in type_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}type')


class MakeFormatTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'format': ['foo', 'bar']}

    def test_formats_are_multivalued(self):
        format_elements = oai_dc_openaire.make_format(self.resource)
        self.assertEqual(len(format_elements), 2)

    def test_formats_are_ordered(self):
        format_elements = oai_dc_openaire.make_format(self.resource)
        self.assertEqual(format_elements[0].text, 'foo')
        self.assertEqual(format_elements[1].text, 'bar')

    def test_formats_have_no_attrs(self):
        format_elements = oai_dc_openaire.make_format(self.resource)
        for element in format_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        format_elements = oai_dc_openaire.make_format(self.resource)
        for element in format_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}format')


class MakeIdentifierTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'identifier': ['foo', 'bar']}

    def test_identifiers_are_multivalued(self):
        identifier_elements = oai_dc_openaire.make_identifier(self.resource)
        self.assertEqual(len(identifier_elements), 2)

    def test_identifiers_are_ordered(self):
        identifier_elements = oai_dc_openaire.make_identifier(self.resource)
        self.assertEqual(identifier_elements[0].text, 'foo')
        self.assertEqual(identifier_elements[1].text, 'bar')

    def test_identifiers_have_no_attrs(self):
        identifier_elements = oai_dc_openaire.make_identifier(self.resource)
        for element in identifier_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        identifier_elements = oai_dc_openaire.make_identifier(self.resource)
        for element in identifier_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}identifier')


class MakeLanguageTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'language': ['foo', 'bar']}

    def test_languages_are_multivalued(self):
        language_elements = oai_dc_openaire.make_language(self.resource)
        self.assertEqual(len(language_elements), 2)

    def test_languages_are_ordered(self):
        language_elements = oai_dc_openaire.make_language(self.resource)
        self.assertEqual(language_elements[0].text, 'foo')
        self.assertEqual(language_elements[1].text, 'bar')

    def test_languages_have_no_attrs(self):
        language_elements = oai_dc_openaire.make_language(self.resource)
        for element in language_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        language_elements = oai_dc_openaire.make_language(self.resource)
        for element in language_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}language')


class MakeMetadataTests(unittest.TestCase):
    def setUp(self):
        self.resource = {
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
                }

    def test_xml_creation(self):
        metadata = oai_dc_openaire.make_metadata(self.resource)

        self.assertEqual(metadata.tag, 'metadata')


class MakeSourceTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'source': ['foo', 'bar']}

    def test_sources_are_multivalued(self):
        source_elements = oai_dc_openaire.make_source(self.resource)
        self.assertEqual(len(source_elements), 2)

    def test_sources_are_ordered(self):
        source_elements = oai_dc_openaire.make_source(self.resource)
        self.assertEqual(source_elements[0].text, 'foo')
        self.assertEqual(source_elements[1].text, 'bar')

    def test_sources_have_no_attrs(self):
        source_elements = oai_dc_openaire.make_source(self.resource)
        for element in source_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        source_elements = oai_dc_openaire.make_source(self.resource)
        for element in source_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}source')


class MakeRightsTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'rights': ['foo', 'bar']}

    def test_rights_are_multivalued(self):
        rights_elements = oai_dc_openaire.make_rights(self.resource)
        self.assertEqual(len(rights_elements), 2)

    def test_rights_are_ordered(self):
        rights_elements = oai_dc_openaire.make_rights(self.resource)
        self.assertEqual(rights_elements[0].text, 'foo')
        self.assertEqual(rights_elements[1].text, 'bar')

    def test_rights_have_no_attrs(self):
        rights_elements = oai_dc_openaire.make_rights(self.resource)
        for element in rights_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        rights_elements = oai_dc_openaire.make_rights(self.resource)
        for element in rights_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}rights')


class MakeSubjectTests(unittest.TestCase):
    def setUp(self):
        self.resource = {'subject': [('en', 'foo'), ('en', 'bar')]}

    def test_subjects_are_multivalued(self):
        subjects_elements = oai_dc_openaire.make_subject(self.resource)
        self.assertEqual(len(subjects_elements), 2)

    def test_subjects_are_ordered(self):
        subjects_elements = oai_dc_openaire.make_subject(self.resource)
        self.assertEqual(subjects_elements[0].text, 'foo')
        self.assertEqual(subjects_elements[1].text, 'bar')

    def test_subjects_have_no_attrs(self):
        subjects_elements = oai_dc_openaire.make_subject(self.resource)
        for element in subjects_elements:
            self.assertEqual(element.attrib, {})

    def test_dc_namespace(self):
        subjects_elements = oai_dc_openaire.make_subject(self.resource)
        for element in subjects_elements:
            self.assertEqual(element.tag,
                    '{http://purl.org/dc/elements/1.1/}subject')

