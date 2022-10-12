import abc
from unittest import TestCase

import numpy as np

from emissor.representation.annotation import Entity
from emissor.representation.scenario import Annotation, class_type, module_source


class TestScenarioModule(TestCase):
    def test_annotation_from_object(self):
        annotation_value = Entity("uri:test")
        annotation = Annotation(class_type(annotation_value), annotation_value, module_source(__name__), 0)

        self.assertEqual("python-type:emissor.representation.annotation.Entity", annotation.type)
        self.assertEqual("python-source:test_scenario", annotation.source)

    def test_class_type_from_metaclass(self):
        """Test that class type is not resolved to abc.ABCMeta"""
        class TestABC(abc.ABC):
            pass

        class TestClass(TestABC):
            def __init__(self, name):
                self.name = name

            @classmethod
            def factory(cls):
                return cls(class_type(cls))

        annotation_value = TestClass.factory()
        annotation = Annotation(class_type(annotation_value), annotation_value, module_source(__name__), 0)

        self.assertRegexpMatches(annotation.type, ".*[.]TestScenarioModule.test_class_type_from_metaclass.<locals>.TestClass")
        self.assertEqual(annotation_value.name, annotation.type)
        self.assertEqual(annotation_value.name, class_type(TestClass))

    def test_annotation_from_numpy(self):
        annotation_value = np.array([])
        annotation = Annotation(class_type(annotation_value), annotation_value, module_source(np.__name__), 0)

        self.assertEqual("python-type:numpy.ndarray", annotation.type)
        self.assertRegexpMatches(annotation.source, "python-source:numpy#\d[.][\w.]+")