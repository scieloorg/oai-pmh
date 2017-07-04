from datetime import datetime

from oaipmh.datastores import Resource


SAMPLE_RESOURCE_DATA = {
        'ridentifier': 'oai:arXiv:cs/0112017',
        'datestamp': datetime.strptime('2017-06-14', '%Y-%m-%d'),
        'setspec': ['set1', 'set2'],
        'title': [('en', 'MICROBIAL COUNTS OF DARK RED...')],
        'creator': ['Vieira, Francisco Cleber Sousa'],
        'subject': [('en', 'bacteria'), ('pt', 'bactéria')],
        'description': [('en', 'The number of colony forming units (CFU)...')],
        'publisher': ['Sociedade Brasileira de Microbiologia'],
        'contributor': ['Evans, R. J.'],
        'date': [datetime.strptime('1998-09-01', '%Y-%m-%d')],
        'type': ['research-article'],
        'format': ['text/html'],
        'identifier': ['https://ref.scielo.org/7vy47j'],
        'source': ['Revista de Microbiologia v.29 n.3 1998'],
        'language': ['en'],
        'relation': [],
        'rights': ['http://creativecommons.org/licenses/by-nc/4.0/'],
        }


def get_sample_resource(**kwargs):
    data = dict(SAMPLE_RESOURCE_DATA)
    data.update(**kwargs)
    return Resource(**data)

