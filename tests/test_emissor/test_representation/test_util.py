from dataclasses import dataclass
from typing import Union, Optional
from unittest import TestCase

from emissor.representation.util import marshal, unmarshal


class TestMarshalling(TestCase):
    def test_plain(self):
        @dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        unmarshalled = unmarshal(marshal(instance), TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEquals(unmarshalled.label, "testString")

    def test_with_nested(self):
        @dataclass
        class TestString:
            label: str

        @dataclass
        class NestTest:
            nested: TestString

        instance = NestTest(TestString("testString"))
        unmarshalled = unmarshal(marshal(instance), NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestString)
        self.assertEquals(unmarshalled.nested.label, "testString")

    def test_with_nested_union(self):
        @dataclass
        class TestString:
            label: str

        @dataclass
        class TestInt:
            id: int

        @dataclass
        class NestTest:
            nested: Union[TestString, TestInt]

        instance = NestTest(TestString("testString"))
        unmarshalled = unmarshal(marshal(instance), NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestString)
        self.assertEquals(unmarshalled.nested.label, "testString")

        instance = NestTest(TestInt(5))
        unmarshalled = unmarshal(marshal(instance), NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestInt)
        self.assertEquals(unmarshalled.nested.id, 5)

    def test_with_none_value(self):
        @dataclass
        class TestString:
            label: Optional[str]

        instance = TestString(None)
        unmarshalled = unmarshal(marshal(instance), TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEquals(unmarshalled.label, None)

    def test_json_with_missing_property(self):
        @dataclass
        class TestString:
            label: Optional[str]

        unmarshalled = unmarshal("{}", TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEquals(unmarshalled.label, None)

    def test_json_to_namedtuple(self):
        @dataclass
        class TestString:
            label: Optional[str]

        unmarshalled = unmarshal('{"label": "testString"}')

        self.assertNotIsInstance(unmarshalled, TestString)
        self.assertEquals(unmarshalled.label, "testString")

    def test_json_with_missing_property_to_namedtuple(self):
        @dataclass
        class TestString:
            label: Optional[str]

        unmarshalled = unmarshal("{}")

        self.assertRaises(AttributeError, lambda: unmarshalled.label)
