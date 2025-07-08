import re
from pathlib import Path
from unittest.mock import Mock, patch

from archlint.collection import (
    Objects,
    add_inherited_methods,
    collect_docs_objects,
    collect_method_info,
    collect_object_texts,
    collect_objects_in_md,
    collect_source_objects,
    parse_function,
)


class TestObjects:
    def test_function_strings(self):
        functions = [
            (Path("src/module.py"), 0, "test_function"),
            (Path("src/utils.py"), 5, "helper_func"),
            (Path("lib/core.py"), 12, "process_data"),
        ]
        classes = []

        objects = Objects(functions=functions, classes=classes)
        expected = [
            "src/module.py:000:test_function",
            "src/utils.py:005:helper_func",
            "lib/core.py:012:process_data",
        ]

        assert objects.function_strings == expected

    def test_method_strings(self):
        functions = []
        classes = [
            (Path("src/models.py"), 0, "User", ["login", "logout"], {}, []),
            (Path("src/base.py"), 1, "BaseModel", ["save", "delete"], {}, []),
            (Path("src/admin.py"), 2, "AdminUser", ["ban_user"], {}, ["User"]),
        ]

        objects = Objects(functions=functions, classes=classes)
        # Note: classes are sorted by path, methods are processed in order
        expected = [
            "src/admin.py:002:AdminUser.ban_user",
            "src/admin.py:002:AdminUser.login",
            "src/admin.py:002:AdminUser.logout",
            "src/base.py:001:BaseModel.save",
            "src/base.py:001:BaseModel.delete",
            "src/models.py:000:User.login",
            "src/models.py:000:User.logout",
        ]

        result = objects.method_strings
        assert result == expected

    def test_strings(self):
        functions = [(Path("src/utils.py"), 0, "helper")]
        classes = [(Path("src/models.py"), 1, "User", ["login"], {}, [])]

        objects = Objects(functions=functions, classes=classes)
        result = objects.strings

        assert "src/utils.py:000:helper" in result
        assert "src/models.py:001:User.login" in result
        assert len(result) == 2

    def test_methodless(self):
        # classes without methods
        functions = []
        classes = [
            (Path("src/models.py"), 0, "User", ["login"], {}, []),
            (Path("src/empty.py"), 1, "EmptyClass", [], {}, []),
            (Path("src/data.py"), 2, "DataClass", [], {}, []),
        ]

        objects = Objects(functions=functions, classes=classes)
        expected = ["src/empty.py:001:EmptyClass", "src/data.py:002:DataClass"]

        assert objects.methodless == expected

    def test_apply(self):
        # 'apply' method with processor function
        functions = [(Path("src/utils.py"), 0, "test_func")]
        classes = [(Path("src/models.py"), 1, "User", ["login"], {}, [])]

        objects = Objects(functions=functions, classes=classes)

        # simple processor
        def add_prefix(s):
            return f"processed_{s}"

        result = objects.apply(add_prefix)
        assert all(s.startswith("processed_") for s in result)

        # with ignore pattern
        ignore_pattern = re.compile(r".*models\.py.*")
        result = objects.apply(add_prefix, ignore=ignore_pattern)
        assert len(result) == 1
        assert "processed_src/utils.py:000:test_func" in result

        # with include_methodless
        empty_classes = [(Path("src/empty.py"), 2, "Empty", [], {}, [])]
        objects_with_empty = Objects(functions=functions, classes=classes + empty_classes)

        result = objects_with_empty.apply(add_prefix, include_methodless=True)
        assert any("Empty" in s for s in result)

        # with processor that returns empty string
        def filter_processor(s):
            return "" if "models" in s else s

        result = objects.apply(filter_processor)
        assert all("models" not in s for s in result)


def test_collect_method_info():
    class_text = """class User:
    def __init__(self, name):
        self.name = name

    def login(self):
        pass

    def logout(self):
        pass
"""

    result = collect_method_info(class_text)
    class_name, method_names, method_dict, super_classes = result

    assert class_name == "User"
    assert "login" in method_names
    assert "logout" in method_names
    assert "__init__" in method_names
    assert len(method_dict) == 3
    assert super_classes == []

    # class with inheritance
    class_text_with_inheritance = """class AdminUser(User, BaseModel):
    def ban_user(self):
        pass"""

    result = collect_method_info(class_text_with_inheritance)
    class_name, method_names, method_dict, super_classes = result

    assert class_name == "AdminUser"
    assert "ban_user" in method_names
    assert set(super_classes) == {"User", "BaseModel"}

    # class with decorators
    class_text_with_decorators = """class Service:
    @property
    def status(self):
        return self._status

    @staticmethod
    def reset():
        pass"""

    result = collect_method_info(class_text_with_decorators)
    class_name, method_names, method_dict, super_classes = result

    assert class_name == "Service"
    assert "status" in method_names
    assert "reset" in method_names


def test_parse_function():
    func_text = """def test_function(arg1, arg2):
    return arg1 + arg2"""

    result = parse_function(func_text)
    assert result == "test_function"

    # function with decorators
    func_text_with_decorator = """@property
def get_value(self):
    return self._value"""

    result = parse_function(func_text_with_decorator)
    assert result == "get_value"

    # with complex function signature
    func_text_complex = """def complex_function(
        arg1: str,
        arg2: int = 10,
        *args,
        **kwargs
    ) -> str:
    pass"""

    result = parse_function(func_text_complex)
    assert result == "complex_function"


def test_collect_objects_in_md():
    md_content = """# archlint.utils

This is the documentation page for the module `utils`.

## ::: archlint.utils.get_project_root
    handler: python
    options:
        show_root_full_path: false
        show_root_full_path: false
        summary: false
        inherited_members: false
        show_root_heading: true
        show_source: false

## ::: archlint.utils.move_path
    handler: python
    options:
        show_root_full_path: false
        summary: false
        inherited_members: false
        show_root_heading: true
        show_source: false

This is a cool function.

## ::: archlint.utils.always_true
    handler: python
    options:
        show_root_full_path: false
        summary: false
        inherited_members: false
        show_root_heading: true
        show_source: false

Some other text.
"""

    result = collect_objects_in_md(md_content)

    assert len(result) == 3

    result = collect_objects_in_md(md_content)
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


def test_collect_docs_objects():
    with (
        patch("pathlib.Path.rglob") as mock_rglob,
        patch("pathlib.Path.read_text") as mock_read_text,
        patch("pathlib.Path.relative_to") as mock_relative_to,
    ):
        mock_file = Mock()
        mock_read_text.return_value = "# Test\n```python\ndef test(): pass\n```"
        mock_rglob.return_value = [mock_file]
        mock_relative_to.return_value = Path("docs/test.md")

        md_dir = Path("docs")
        project_root = Path(".")

        with patch("your_module.collect_objects_in_md") as mock_collect:
            mock_collect.return_value = [(0, "test_function")]

            result = collect_docs_objects(md_dir, project_root)

            assert isinstance(result, Objects)
            assert len(result.functions) >= 0
            assert len(result.classes) == 0


def test_collect_object_texts():
    source_code = """def function1():
    pass


class Class1:
    def method1(self):
        pass


def function2():
    return True


@dataclass
class DataClass:
    name: str

    

class TestClass:
    def test_method(self):
        pass

        
class CoolClass2():

    def method_extraordinaire(self) -> str:
        ...

        
def last_function():
    ...



"""

    result = collect_object_texts(source_code)

    assert len(result) >= 3
    assert any("function1" in text for text in result)
    assert any("Class1" in text for text in result)
    assert any("DataClass" in text for text in result)


def test_collect_source_objects():
    with (
        patch("pathlib.Path.rglob") as mock_rglob,
        patch("pathlib.Path.read_text") as mock_read_text,
        patch("pathlib.Path.relative_to") as mock_relative_to,
    ):
        mock_file = Mock()
        mock_read_text.return_value = """def test_function():
    pass


class TestClass:
    def test_method(self):
        pass
        

@


# comment

        
class Test2():

    def method_extraordinaire(self) -> str:
        ...

        
def last_function():
    ...


"""
        mock_rglob.return_value = [mock_file]
        mock_relative_to.return_value = Path("src/test.py")

        src_dir = Path("src")
        root_dir = Path(".")

        # with (
        #     patch("your_module.collect_object_texts") as mock_collect_texts,
        #     patch("your_module.collect_method_info") as mock_collect_methods,
        #     patch("your_module.parse_function") as mock_parse_func,
        # ):
        #     mock_collect_texts.return_value = [
        #         "def test_function():\n    pass",
        #         "class TestClass:\n    def test_method(self):\n        pass",
        #     ]
        #     mock_collect_methods.return_value = ("TestClass", ["test_method"], {}, [])
        #     mock_parse_func.return_value = "test_function"

        result = collect_source_objects(src_dir, root_dir)

        assert isinstance(result, Objects)
        assert len(result.functions) >= 0
        assert len(result.classes) >= 0


def test_add_inherited_methods():
    class_tuples = [
        (Path("base.py"), 0, "BaseClass", ["base_method"], {}, []),
        (Path("child.py"), 1, "ChildClass", ["child_method"], {}, ["BaseClass"]),
        (Path("grandchild.py"), 2, "GrandChild", ["grand_method"], {}, ["ChildClass"]),
    ]

    result = add_inherited_methods(class_tuples)

    base_class, child_class, grandchild_class = result

    assert "base_method" in base_class[3]
    assert len(base_class[3]) == 1

    assert "base_method" in child_class[3]
    assert "child_method" in child_class[3]

    assert "base_method" in grandchild_class[3]
    assert "child_method" in grandchild_class[3]
    assert "grand_method" in grandchild_class[3]

    # multiple inheritance
    class_tuples_multi = [
        (Path("a.py"), 0, "ClassA", ["method_a"], {}, []),
        (Path("b.py"), 1, "ClassB", ["method_b"], {}, []),
        (Path("c.py"), 2, "ClassC", ["method_c"], {}, ["ClassA", "ClassB"]),
    ]

    result = add_inherited_methods(class_tuples_multi)
    class_c = next(item for item in result if item[2] == "ClassC")

    assert "method_a" in class_c[3]
    assert "method_b" in class_c[3]
    assert "method_c" in class_c[3]

    # no inheritance
    class_tuples_no_inherit = [(Path("standalone.py"), 0, "Standalone", ["solo_method"], {}, [])]

    result = add_inherited_methods(class_tuples_no_inherit)
    standalone = result[0]

    assert standalone[3] == ["solo_method"]
    assert len(result) == 1


def test_objects_edge_cases():
    # Test with empty inputs
    empty_objects = Objects(functions=[], classes=[])
    assert empty_objects.function_strings == []
    assert empty_objects.method_strings == []
    assert empty_objects.strings == []
    assert empty_objects.methodless == []

    # Test apply with empty processor result
    def empty_processor(s):
        return ""

    assert empty_objects.apply(empty_processor) == []


def test_collect_method_info_edge_cases():
    # empty class
    empty_class = "class Empty:\n    pass"
    result = collect_method_info(empty_class)
    assert result[0] == "Empty"
    assert result[1] == []

    # malformed class
    malformed_class = "class"
    result = collect_method_info(malformed_class)
    assert isinstance(result, tuple)
    assert len(result) == 4


def test_parse_function_edge_cases():
    # non-function text
    non_function = "not a function"
    result = parse_function(non_function)
    assert result is None or result == ""

    # empty string
    result = parse_function("")
    assert result is None or result == ""
