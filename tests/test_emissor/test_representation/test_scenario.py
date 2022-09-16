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

    def test_annotation_from_numpy(self):
        annotation_value = np.array([])
        annotation = Annotation(class_type(annotation_value), annotation_value, module_source(np.__name__), 0)

        self.assertEqual("python-type:numpy.ndarray", annotation.type)
        self.assertRegexpMatches(annotation.source, "python-source:numpy#\d[.][\w.]+")