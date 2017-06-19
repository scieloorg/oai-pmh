import unittest

from .fixtures import factories
from oaipmh import datastores


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

