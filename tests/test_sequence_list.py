from aligned_textgrid import SequenceList, SequenceInterval, SequencePoint, custom_classes
import numpy as np
import pytest

def make_sequences(cls, n)->list[SequenceInterval]:
    starts, step = np.linspace(0, 20, num = n, retstep=True)
    ends = starts + step

    labels = [f"lab_{x}" for x in np.arange(n)]

    out_list = []
    for start, end, label in zip(starts, ends, labels):
        if issubclass(cls, SequenceInterval):
            out_list += [cls((start, end, label))]
        
        if issubclass(cls, SequencePoint):
            out_list += [cls((start, label))]
    return out_list
    
class TestSequenceList:
    def test_interval_list(self):
        MyInterval, = custom_classes(["MyInterval"])
        my_list = SequenceList(
            MyInterval((2,4, "a"))
        )

        assert issubclass(my_list.entry_class, MyInterval)

        new_interval = MyInterval((0, 1, "b"))
        my_list.append(new_interval)

        assert new_interval in my_list

        # check the result is properly sorted
        assert my_list.index(new_interval) == 0

        next_interval = MyInterval((5, 10, "c"))

        my_list += [next_interval]

        assert new_interval in my_list
        assert next_interval in my_list

    def test_point_list(self):
        MyPoint, = custom_classes(["MyPoint"], points = [0])

        my_list = SequenceList(MyPoint((5, "a")))
        assert issubclass(my_list.entry_class, MyPoint)

        new_point = MyPoint((0, "b"))
        my_list.append(new_point)

        assert new_point in my_list
        assert my_list.index(new_point) == 0

        next_point = MyPoint((10, "c"))

        my_list += [next_point]
        
        assert new_point in my_list
        assert next_point in my_list
    
    def test_strictnes(self):
        MyWord, MyPhone, MyPoint = custom_classes(["MyWord", "MyPhone", "MyPoint"], points=[2])

        word_list = SequenceList(*make_sequences(MyWord, 20))
        mix_list = make_sequences(MyWord, 5) + make_sequences(MyPhone, 5)

        with pytest.raises(ValueError):
            word_list.append(MyPhone((0,3,"x")))

        with pytest.raises(ValueError):
            word_list += [MyPhone((0,3, "x"))]
        
        with pytest.raises(ValueError):
            word_list.append(MyPoint((0,"x")))

        with pytest.raises(ValueError):
            new_list = SequenceList()
            new_list += mix_list
    
    def test_properties(self):
        MyWord, MyPoint  = custom_classes(["MyWord", "MyPoint"], points=[1])
        n = 10

        my_list = SequenceList()
        my_point_list = SequenceList()
        assert len(my_list.labels) == 0
        assert len(my_list.starts) == 0
        assert len(my_list.ends) == 0

        word_list = make_sequences(MyWord, n)
        point_list = make_sequences(MyPoint, n)
        
        my_list += word_list
        my_point_list += point_list

        assert len(my_list.labels) == n
        assert len(my_list.starts) == n
        assert len(my_list.ends) == n

        assert len(my_point_list.labels) == n
        assert len(my_point_list.starts) == n
        assert len(my_point_list.ends) == n


    def test_pop_remove(self):
        MyWord, = custom_classes(["MyWord"])
        word_list = make_sequences(MyWord, 20)
        first_word = word_list[0]
        second_word = word_list[1]

        my_list = SequenceList(*word_list)

        assert first_word in my_list
        assert second_word in my_list

        my_list.pop(first_word)
        assert not first_word in my_list

        my_list.remove(second_word)
        assert not second_word in my_list

    def test_remove_super_instance(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])

        word = MyWord((0,5, "a"))
        phones = [
            MyPhone((0,2,"A")),
            MyPhone((2,5, "AA"))
        ]

        for p in phones:
            word.append(p)

        assert phones[0] in word
        assert phones[0].super_instance is word

        word.subset_list.remove(phones[0])

        assert not phones[0] in word
        assert not phones[0].super_instance is word

    def test_concat(self):
        MyWord, = custom_classes(["MyWord"])

        n = 5

        words1 = make_sequences(MyWord, n)
        words2 = make_sequences(MyWord, n)

        my_list1 = SequenceList(*words1)
        my_list2 = SequenceList(*words2)

        orig_end = my_list1.ends.max()

        my_list1.concat(my_list2)

        assert len(my_list1) == (n*2)
        assert my_list1.ends.max() == orig_end + orig_end



    pass
