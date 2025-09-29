import json
import pickle
import uuid
from dataclasses import dataclass
from datetime import datetime, date
from typing import Union, Optional
from unittest import TestCase

from emissor.representation.ldschema import emissor_dataclass, EMISSOR_NAMESPACE, LdProperty
from emissor.representation.util import marshal, unmarshal, PickleableDict


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

    def test_datetime(self):
        @dataclass
        class TestDate:
            date: datetime

        now = datetime.now()
        instance = TestDate(now)
        self.assertRaises(TypeError, lambda: marshal(instance, default=vars))

        unmarshalled = unmarshal(marshal(instance, cls=TestDate), cls=TestDate)
        self.assertIsInstance(unmarshalled, TestDate)
        self.assertIsInstance(unmarshalled.date, datetime)
        self.assertEquals(unmarshalled.date, now)

    def test_date(self):
        @dataclass
        class TestDate:
            date: date

        now = date.today()
        instance = TestDate(now)
        unmarshalled = unmarshal(marshal(instance, cls=TestDate), cls=TestDate)

        self.assertIsInstance(unmarshalled, TestDate)
        self.assertEqual(unmarshalled.date, now)


class TestMarshallingWithoutTypes(TestCase):
    def test_plain(self):
        @dataclass
        class TestString:
            label: str

        instance = TestString("testString")
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, TestString)
        self.assertEqual(unmarshalled.label, "testString")

    def test_datetime(self):
        @dataclass
        class TestDate:
            date: datetime

        now = datetime.now()
        instance = TestDate(now)
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, TestDate)
        self.assertEqual(unmarshalled.date, now.isoformat())

    def test_date(self):
        @dataclass
        class TestDate:
            date: date

        now = date.today()
        instance = TestDate(now)
        unmarshalled = unmarshal(marshal(instance))

        self.assertNotIsInstance(unmarshalled, TestDate)
        self.assertEqual(unmarshalled.date, now.isoformat())

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


class TestPickleableDict(TestCase):
    def test_basic_dict_functionality(self):
        """Test that PickleableDict works as a regular dictionary"""
        pd = PickleableDict({'a': 1, 'b': 2})

        self.assertEqual(pd['a'], 1)
        self.assertEqual(pd['b'], 2)
        self.assertEqual(len(pd), 2)
        self.assertIn('a', pd)
        self.assertNotIn('c', pd)

        pd['c'] = 3
        self.assertEqual(pd['c'], 3)
        self.assertEqual(len(pd), 3)

        del pd['c']
        self.assertEqual(len(pd), 2)
        self.assertNotIn('c', pd)

    def test_attribute_access(self):
        """Test that PickleableDict supports attribute-style access"""
        pd = PickleableDict({'label': 'test', 'value': 42})

        # Test attribute access for reading
        self.assertEqual(pd.label, 'test')
        self.assertEqual(pd.value, 42)

        # Test attribute access for writing
        pd.new_attr = 'new_value'
        self.assertEqual(pd['new_attr'], 'new_value')
        self.assertEqual(pd.new_attr, 'new_value')

        # Test modification via attribute access
        pd.label = 'modified'
        self.assertEqual(pd['label'], 'modified')
        self.assertEqual(pd.label, 'modified')

    def test_attribute_errors(self):
        """Test that AttributeError is raised for non-existent attributes"""
        pd = PickleableDict({'a': 1})

        with self.assertRaises(AttributeError):
            _ = pd.nonexistent

        with self.assertRaises(AttributeError):
            del pd.nonexistent

    def test_pickling(self):
        """Test that PickleableDict can be pickled and unpickled"""
        original = PickleableDict({'label': 'test', 'value': 42, 'nested': {'inner': 'data'}})

        # Pickle and unpickle
        pickled_data = pickle.dumps(original)
        unpickled = pickle.loads(pickled_data)

        # Verify the unpickled object
        self.assertIsInstance(unpickled, PickleableDict)
        self.assertEqual(unpickled['label'], 'test')
        self.assertEqual(unpickled['value'], 42)
        self.assertEqual(unpickled['nested'], {'inner': 'data'})

        # Verify attribute access still works
        self.assertEqual(unpickled.label, 'test')
        self.assertEqual(unpickled.value, 42)

    def test_property_handling(self):
        """Test that PickleableDict handles property assignment correctly"""
        class TestClass(PickleableDict):
            @property
            def read_only_prop(self):
                return "read_only"

            @property
            def read_write_prop(self):
                return self.get('_read_write_prop', 'default')

            @read_write_prop.setter
            def read_write_prop(self, value):
                self['_read_write_prop'] = value

        obj = TestClass({'a': 1})

        # Test read-only property
        self.assertEqual(obj.read_only_prop, "read_only")

        # Attempting to set read-only property should store in dict instead
        obj.read_only_prop = "new_value"
        self.assertEqual(obj['read_only_prop'], "new_value")
        # Property getter should still return original value
        # (Note: This tests the fallback behavior for read-only properties)

        # Test read-write property
        self.assertEqual(obj.read_write_prop, "default")
        obj.read_write_prop = "new_value"
        self.assertEqual(obj.read_write_prop, "new_value")
        self.assertEqual(obj['_read_write_prop'], "new_value")

    def test_has_keys_method(self):
        """Test that PickleableDict has keys() method required by emissor marshal"""
        pd = PickleableDict({'a': 1, 'b': 2})

        keys = pd.keys()
        self.assertIn('a', keys)
        self.assertIn('b', keys)
        self.assertEqual(len(list(keys)), 2)

    def test_unmarshal_compatibility(self):
        """Test that unmarshal creates PickleableDict objects correctly"""
        json_data = '{"label": "test", "value": 42}'
        result = unmarshal(json_data)

        self.assertIsInstance(result, PickleableDict)
        self.assertEqual(result.label, "test")
        self.assertEqual(result.value, 42)
        self.assertEqual(result['label'], "test")
        self.assertEqual(result['value'], 42)

    def test_nested_unmarshal_compatibility(self):
        """Test that nested objects are also converted to PickleableDict"""
        json_data = '{"outer": {"inner": "value", "number": 123}}'
        result = unmarshal(json_data)

        self.assertIsInstance(result, PickleableDict)
        self.assertIsInstance(result.outer, PickleableDict)

        self.assertEqual(result.outer.inner, "value")
        self.assertEqual(result.outer.number, 123)
        self.assertEqual(result.outer['inner'], "value")
        self.assertEqual(result.outer['number'], 123)

    def test_backwards_compatibility_with_marshal(self):
        """Test that PickleableDict works with marshal function"""
        @dataclass
        class TestData:
            name: str
            value: int

        instance = TestData("test", 42)
        json_str = marshal(instance)
        result = unmarshal(json_str)

        # Result should be PickleableDict with attribute access
        self.assertIsInstance(result, PickleableDict)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.value, 42)

        # Should also support dictionary access
        self.assertEqual(result['name'], "test")
        self.assertEqual(result['value'], 42)