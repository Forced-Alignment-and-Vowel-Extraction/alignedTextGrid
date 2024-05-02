import pytest
from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.sequences.tiers import *
from aligned_textgrid.custom_classes import custom_classes, clone_class, get_class_hierarchy
from aligned_textgrid.aligned_textgrid import AlignedTextGrid

class TestCustomCreation:

    def test_default_creation(self):
        ClassA, ClassB = custom_classes(class_list=["ClassA", "ClassB"])
        assert issubclass(ClassA, SequenceInterval)
        assert issubclass(ClassB, SequenceInterval)
        assert ClassA.__name__ == "ClassA"
        assert ClassB.__name__ == "ClassB"
        assert issubclass(ClassA.superset_class, Top)
        assert ClassA.subset_class is ClassB
        assert ClassB.superset_class is ClassA
        assert issubclass(ClassB.subset_class, Bottom)

    def test_custom_return_idx(self):
        ClassA, ClassB = custom_classes(
            class_list=["ClassB", "ClassA"],
            return_order=[1,0]
            )
        assert issubclass(ClassA, SequenceInterval)
        assert issubclass(ClassB, SequenceInterval)
        assert ClassA.__name__ == "ClassA"
        assert ClassB.__name__ == "ClassB"
        assert issubclass(ClassB.superset_class, Top)
        assert ClassB.subset_class is ClassA
        assert ClassA.superset_class is ClassB
        assert issubclass(ClassA.subset_class, Bottom)

    def test_custom_return_char(self):
        ClassA, ClassB = custom_classes(
            class_list=["ClassB", "ClassA"],
            return_order=["ClassA", "ClassB"]
            )
        
        assert issubclass(ClassA, SequenceInterval)
        assert issubclass(ClassB, SequenceInterval)
        assert ClassA.__name__ == "ClassA"
        assert ClassB.__name__ == "ClassB"
        assert issubclass(ClassB.superset_class, Top)
        assert ClassB.subset_class is ClassA
        assert ClassA.superset_class is ClassB
        assert issubclass(ClassA.subset_class, Bottom)
        
class TestCustomUse:

    def test_custom_read_one(self):
        try:
            tg_one = AlignedTextGrid(
                textgrid_path="tests/test_data/josef-fruehwald_speaker.TextGrid",
                entry_classes=custom_classes(["MyWord", "MyPhone"])
            )
        except:
            assert False
        
        assert tg_one[0][0].entry_class.__name__ == "MyWord"
        assert tg_one[0][1].entry_class.__name__ == "MyPhone"

    def test_custom_read_two(self):
        try:
            tg_two = AlignedTextGrid(
                textgrid_path="tests/test_data/KY25A_1.TextGrid",
                entry_classes=custom_classes(["MyWord2", "MyPhone2"])
            )
        except:
            assert False
        
        assert tg_two[0][0].entry_class.__name__ == "MyWord2"
        assert tg_two[0][1].entry_class.__name__ == "MyPhone2"

class TestCloning:

    def test_clone_class(self):
        Foo, Bar = custom_classes(["Foo", "Bar"])
        Foo2 = clone_class(Foo)

        foo = Foo()
        foo2 = Foo2()

        assert not Foo is Foo2
        assert Foo.subset_class is Bar
        assert not Foo2.subset_class is Bar

        assert issubclass(Foo2, Foo)

        assert isinstance(foo, Foo)
        assert not isinstance(foo, Foo2)
        assert isinstance(foo2, Foo)

class TestGetHierarchy:

    def test_get_hierarchy(self):
        Foo, Bar, Baz = custom_classes(["Foo", "Bar", "Baz"])

        foo_hierarchy = get_class_hierarchy(Foo)
        baz_hierarchy = get_class_hierarchy(Baz)

        for f,b in zip(foo_hierarchy, baz_hierarchy):
            assert f is b