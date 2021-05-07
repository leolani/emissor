from dataclasses import dataclass
from unittest import TestCase

from rdflib import URIRef

from emissor.representation.ldschema import ld_type, LD_CONTEXT_FIELD, LdProperty


class TestSchemaWithoutOntology(TestCase):
    def test_plain_context(self):
        @dataclass
        @ld_type(namespace=URIRef("http://schema.org"))
        class TestClass:
            property: str
            other: str

        instance = TestClass("testProperty", "testOther")
        context = getattr(instance, LD_CONTEXT_FIELD)

        self.assertIn("property", context)
        self.assertEqual(URIRef("http://schema.org#property"), context["property"])
        self.assertIn("other", context)
        self.assertEqual(URIRef("http://schema.org#other"), context["other"])

    def test_plain_type(self):
        @dataclass
        @ld_type(namespace="http://schema.org")
        class TestClass:
            property: str
            other: str

        instance = TestClass("testProperty", "testOther")

        self.assertEqual("TestClass", instance._ld_type)

    def test_nested_object(self):
        @dataclass
        class NestClass:
            property: str

        @dataclass
        @ld_type(namespace="http://schema.org")
        class TestClass:
            nested: NestClass

        instance = TestClass(NestClass("testString"))
        context = getattr(instance, LD_CONTEXT_FIELD)

        self.assertIn("nested", context)
        self.assertEqual(URIRef("http://schema.org#nested"), context["nested"])
        self.assertNotIn("property", context)
        self.assertFalse(hasattr(instance.nested, "_ld_context"))

    def test_nested_ld_type(self):
        @dataclass
        @ld_type(namespace="http://schema.org")
        class NestClass:
            property: str

        @dataclass
        @ld_type(namespace="http://schema.org")
        class TestClass:
            nested: NestClass

        instance = TestClass(NestClass("testString"))
        context = getattr(instance, LD_CONTEXT_FIELD)

        self.assertIn("nested", context)
        self.assertEqual(URIRef("http://schema.org#nested"), context["nested"])
        self.assertNotIn("property", context)

        nested_context = getattr(instance.nested, LD_CONTEXT_FIELD)
        self.assertIn("property", nested_context)
        self.assertEqual(URIRef("http://schema.org#property"), nested_context["property"])
        self.assertNotIn("nested", nested_context)

    def test_property_alias(self):
        @dataclass
        @ld_type(namespace=URIRef("http://schema.org"))
        class TestClass:
            other: str
            property: str = LdProperty(alias="hasProperty")

        instance = TestClass("testProperty", "testOther")
        context = getattr(instance, LD_CONTEXT_FIELD)

        self.assertNotIn("hasProperty", context)
        self.assertEqual(URIRef("http://schema.org#hasProperty"), context["property"])
        self.assertEqual(URIRef("http://schema.org#other"), context["other"])

    def test_class_hierarchy(self):
        @dataclass
        @ld_type(namespace=URIRef("http://schema.org"))
        class TestParent:
            parent_property: str

        @dataclass
        @ld_type(namespace=URIRef("http://schema.org"))
        class TestChild(TestParent):
            child_property: str

        instance = TestChild("testParentProperty", "testChildProperty")
        context = getattr(instance, LD_CONTEXT_FIELD)

        self.assertIn("parent_property", context)
        self.assertEqual(URIRef("http://schema.org#parent_property"), context["parent_property"])
        self.assertIn("child_property", context)
        self.assertEqual(URIRef("http://schema.org#child_property"), context["child_property"])

    def test_class_hierarchy_with_ld_property(self):
        @dataclass
        @ld_type(namespace=URIRef("http://schema.org"))
        class TestParent:
            parent_property: str = LdProperty(alias="hasParentProperty")

        @dataclass
        @ld_type(namespace=URIRef("http://schema.org"))
        class TestChild(TestParent):
            child_property: str = LdProperty(alias="hasChildProperty")

        instance = TestChild("testParentProperty", "testChildProperty")
        context = getattr(instance, LD_CONTEXT_FIELD)

        self.assertNotIn("hasParentProperty", context)
        self.assertEqual(URIRef("http://schema.org#hasParentProperty"), context["parent_property"])
        self.assertNotIn("hasChildProperty", context)
        self.assertEqual(URIRef("http://schema.org#hasChildProperty"), context["child_property"])
