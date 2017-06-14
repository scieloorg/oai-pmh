import unittest

from .fixtures import resources
from oaipmh import datastores


class InMemoryTests(unittest.TestCase):
    def setUp(self):
        self.store = datastores.InMemory()

    def test_new_resource(self):
        resource = resources.get_sample_resource()
        self.store.add(resource)
        self.assertEqual(self.store.get(resource.ridentifier), resource)

    def test_resources_can_be_overrided(self):
        resource = resources.get_sample_resource()
        self.store.add(resource)

        resource2 = resources.get_sample_resource(title=[('pt', 'New title')])
        self.store.add(resource2)

        self.assertEqual(self.store.get(resource.ridentifier), resource2)
        
    def test_missing_resource(self):
        self.assertRaises(datastores.DoesNotExistError, 
                lambda: self.store.get('missing-ridentifier'))

    def test_list_all(self):
        sample_resources = [resources.get_sample_resource(ridentifier='rid-'+str(i))
                            for i in range(100)]

        for resource in sample_resources:
            self.store.add(resource)

        retrieved_resources = list(self.store.list())
        self.assertEqual(sample_resources, retrieved_resources)

    def test_list_single_set(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_resources = [resources.get_sample_resource(**d)
                            for d in data]

        for resource in sample_resources:
            self.store.add(resource)

        set1_resources = list(self.store.list(sets=['set1']))
        self.assertEqual(len(set1_resources), 100)

    def test_list_two_sets(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_resources = [resources.get_sample_resource(**d)
                            for d in data]

        for resource in sample_resources:
            self.store.add(resource)

        set1_resources = list(self.store.list(sets=['set1', 'set2']))
        self.assertEqual(len(set1_resources), 200)

    def test_counted_list(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_resources = [resources.get_sample_resource(**d)
                            for d in data]

        for resource in sample_resources:
            self.store.add(resource)

        set1_resources = list(self.store.list(sets=['set1', 'set2'], count=10))
        self.assertEqual(len(set1_resources), 10)

    def test_offset_list(self):
        data = [{'ridentifier': 'rid'+str(i), 'setspec': ['set1']} 
                for i in range(100)]
        data += [{'ridentifier': 'rid'+str(i), 'setspec': ['set2']} 
                 for i in range(100, 200)]

        sample_resources = [resources.get_sample_resource(**d)
                            for d in data]

        for resource in sample_resources:
            self.store.add(resource)

        set1_resources = list(self.store.list(sets=['set1', 'set2'],
            offset=0, count=10))
        set1_resources += list(self.store.list(sets=['set1', 'set2'],
            offset=10, count=10))
        
        set2_resources = list(self.store.list(sets=['set1', 'set2'],
            offset=0, count=20))
        
        self.assertEqual(set1_resources, set2_resources)

