import json
import uuid
from dataclasses import dataclass
from pprint import pprint
from typing import Union, Optional
from unittest import TestCase

from emissor.representation.ldschema import emissor_dataclass, EMISSOR_NAMESPACE, LdProperty
from emissor.representation.util import marshal, unmarshal


class TestMarshallingWithTypes(TestCase):
    def test_plain(self):
        @dataclass
        class TestString:
            label: str
            json_ld_context: Union[str, dict]

        instance = TestString("testString", {'id': '@id'})

        unmarshalled = unmarshal(marshal(instance, cls=TestString), cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, "testString")

    def test_with_nested(self):
        @dataclass
        class TestString:
            label: str

        @dataclass
        class NestTest:
            nested: TestString

        instance = NestTest(TestString("testString"))
        unmarshalled = unmarshal(marshal(instance, cls=NestTest), cls=NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestString)
        self.assertEqual(unmarshalled.nested.label, "testString")

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
        unmarshalled = unmarshal(marshal(instance, cls=NestTest), cls=NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestString)
        self.assertEqual(unmarshalled.nested.label, "testString")

        instance = NestTest(TestInt(5))
        unmarshalled = unmarshal(marshal(instance, cls=NestTest), cls=NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestInt)
        self.assertEqual(unmarshalled.nested.id, 5)

    def test_with_none_value(self):
        @dataclass
        class TestString:
            label: Optional[str]

        instance = TestString(None)
        unmarshalled = unmarshal(marshal(instance, cls=TestString), cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, None)

    def test_json_with_missing_property(self):
        @dataclass
        class TestString:
            label: Optional[str]

        unmarshalled = unmarshal("{}", cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, None)

    def test_list(self):
        @dataclass(frozen=True)
        class TestString:
            label: str

        instance = [TestString("test1"), TestString("test2")]
        unmarshalled = unmarshal(marshal(instance, cls=TestString), cls=TestString)

        self.assertIsInstance(unmarshalled, list)
        self.assertListEqual(unmarshalled, instance)

    def test_set(self):
        @dataclass(frozen=True)
        class TestString:
            label: str

        instance = {TestString("test1"), TestString("test2")}
        unmarshalled = unmarshal(marshal(instance, cls=TestString), cls=TestString)

        self.assertIsInstance(unmarshalled, list)
        self.assertSetEqual(set(unmarshalled), instance)

    def test_type_unsupported_by_serializer(self):
        @dataclass
        class TestString:
            label: uuid.UUID

        instance = TestString(uuid.uuid4())
        self.assertRaises(TypeError, lambda: marshal(instance, default=vars))

        unmarshalled = unmarshal(marshal(instance, cls=TestString), cls=TestString)
        self.assertIsInstance(unmarshalled, TestString)
        self.assertIsInstance(unmarshalled.label, uuid.UUID)


class TestMarshallingWithoutTypes(TestCase):
    def test_plain(self):
        @dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, "testString")

    def test_with_nested(self):
        @dataclass
        class TestString:
            label: str

        @dataclass
        class NestTest:
            nested: TestString

        instance = NestTest(TestString("testString"))
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, NestTest)
        self.assertNotIsInstance(unmarshalled.nested, TestString)
        self.assertEqual(unmarshalled.nested.label, "testString")

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
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, NestTest)
        self.assertNotIsInstance(unmarshalled.nested, TestString)
        self.assertEqual(unmarshalled.nested.label, "testString")

        instance = NestTest(TestInt(5))
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, NestTest)
        self.assertNotIsInstance(unmarshalled.nested, TestInt)
        self.assertEqual(unmarshalled.nested.id, 5)

    def test_with_none_value(self):
        @dataclass
        class TestString:
            label: Optional[str]

        instance = TestString(None)
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, None)

    def test_json_with_missing_property(self):
        @dataclass
        class TestString:
            label: Optional[str]

        unmarshalled = unmarshal("{}")

        self.assertNotIsInstance(unmarshalled, TestString)
        self.assertRaises(AttributeError, lambda: unmarshalled.label)

    def test_list(self):
        @dataclass(frozen=True)
        class TestString:
            label: str

        instance = [TestString("test1"), TestString("test2")]
        json = marshal(instance)
        unmarshalled = unmarshal(json)

        self.assertIsInstance(unmarshalled, list)
        self.assertListEqual([u.label for u in unmarshalled], [i.label for i in instance])

    def test_set(self):
        @dataclass(frozen=True)
        class TestString:
            label: str

        instance = {TestString("test1"), TestString("test2")}
        json = marshal(instance)
        unmarshalled = unmarshal(json)

        self.assertIsInstance(unmarshalled, list)
        self.assertSetEqual({u.label for u in unmarshalled}, {i.label for i in instance})


class TestOnlyUnmarshallingWithTypes(TestCase):
    def test_plain(self):
        @dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        unmarshalled = unmarshal(marshal(instance), cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, "testString")

    def test_with_nested(self):
        @dataclass
        class TestString:
            label: str

        @dataclass
        class NestTest:
            nested: TestString

        instance = NestTest(TestString("testString"))
        unmarshalled = unmarshal(marshal(instance), cls=NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestString)
        self.assertEqual(unmarshalled.nested.label, "testString")

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
        unmarshalled = unmarshal(marshal(instance), cls=NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestString)
        self.assertEqual(unmarshalled.nested.label, "testString")

        instance = NestTest(TestInt(5))
        unmarshalled = unmarshal(marshal(instance), cls=NestTest)

        self.assertIsInstance(unmarshalled, NestTest)
        self.assertIsInstance(unmarshalled.nested, TestInt)
        self.assertEqual(unmarshalled.nested.id, 5)

    def test_with_none_value(self):
        @dataclass
        class TestString:
            label: Optional[str]

        instance = TestString(None)
        unmarshalled = unmarshal(marshal(instance), cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, None)

    def test_json_with_missing_property(self):
        @dataclass
        class TestString:
            label: Optional[str]

        unmarshalled = unmarshal("{}", cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, None)

    def test_list(self):
        @dataclass(frozen=True)
        class TestString:
            label: str

        instance = [TestString("test1"), TestString("test2")]
        json = marshal(instance)
        unmarshalled = unmarshal(json, cls=TestString)

        self.assertIsInstance(unmarshalled, list)
        self.assertListEqual(unmarshalled, instance)

    def test_set(self):
        @dataclass(frozen=True)
        class TestString:
            label: str

        instance = {TestString("test1"), TestString("test2")}
        json = marshal(instance)
        unmarshalled = unmarshal(json, cls=TestString)

        self.assertIsInstance(unmarshalled, list)
        self.assertSetEqual(set(unmarshalled), instance)


class TestLDMarshalling(TestCase):
    def test_plain(self):
        @emissor_dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        json_string = marshal(instance, cls=TestString)

        obj_dict = json.loads(json_string)
        type_ = obj_dict["@type"]
        context = obj_dict["@context"]

        self.assertEqual("TestString", type_)
        self.assertEqual(EMISSOR_NAMESPACE + "#" + "TestString", context["TestString"])
        self.assertEqual(EMISSOR_NAMESPACE + "#" + "label", context["label"])

    def test_alias(self):
        @emissor_dataclass
        class TestString:
            label: str = LdProperty(alias="name")

        instance = TestString("testString")
        json_string = marshal(instance, cls=TestString)

        obj_dict = json.loads(json_string)
        type_ = obj_dict["@type"]
        context = obj_dict["@context"]

        self.assertEqual("TestString", type_)
        self.assertEqual(EMISSOR_NAMESPACE + "#" + "TestString", context["TestString"])
        self.assertEqual(EMISSOR_NAMESPACE + "#" + "name", context["label"])

    def test_separator(self):
        @emissor_dataclass(separator="/")
        class TestString:
            label: str = LdProperty(alias="name")

        instance = TestString("testString")
        json_string = marshal(instance, cls=TestString)

        obj_dict = json.loads(json_string)
        type_ = obj_dict["@type"]
        context = obj_dict["@context"]

        self.assertEqual("TestString", type_)
        self.assertEqual(EMISSOR_NAMESPACE + "/" + "TestString", context["TestString"])
        self.assertEqual(EMISSOR_NAMESPACE + "/" + "name", context["label"])

    def test_unmarshall_type(self):
        @emissor_dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        unmarshalled = unmarshal(marshal(instance, cls=TestString), cls=TestString)

        self.assertIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, "testString")

    def test_unmarshall_without_type(self):
        @emissor_dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        unmarshalled = unmarshal(marshal(instance, cls=TestString))

        self.assertEqual(unmarshalled.label, "testString")