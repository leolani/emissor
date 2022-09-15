from unittest import TestCase

from emissor.representation.annotation import Entity
from emissor.representation.scenario import Annotation, class_type, module_source


class TestScenarioModule(TestCase):
    def test_annotation_from_object(self):
        annotation_value = Entity("uri:test")
        annotation = Annotation(class_type(annotation_value), annotation_value, module_source(__name__), 0)

        self.assertEqual("emissor.representation.annotation.Entity", annotation.type)
        self.assertEqual("test_scenario", annotation.source)