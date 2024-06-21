from aligned_textgrid import SequenceInterval, \
    SequencePoint, \
    SequenceTier, \
    SequencePointTier,\
    TierGroup,\
    PointsGroup,\
    AlignedTextGrid,\
    custom_classes
import numpy as np

import pytest

class TestSequenceInterval:

    def test_solo_add(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])

        word = MyWord((0, 10, "a"))
        phone1 = MyPhone((0, 5, "A"))
        phone2 = MyPhone((5, 10, "AA"))

        # + breaks reference of the addee
        word2 = word

        word += phone1
        phone2 += word

        assert phone1 in word
        assert phone2 in word
        assert not word2 is word
        
        assert phone1.fol is phone2
    
    def test_point_add(self):
        MyPoint, = custom_classes(["MyPoint"], points = [0])
        point1 = MyPoint((0,"a"))
        point2 = MyPoint((1,"b"))

        with pytest.warns():
            point1 + point2

        with pytest.warns():
            point1.append(point2)

    def test_solo_append(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word = MyWord((0, 10, "a"))
        phone1 = MyPhone((0, 5, "A"))
        phone2 = MyPhone((5, 10, "AA"))

        # append does not break reference
        word2 = word

        word.append(phone1)
        word.append(phone2)

        assert phone1 in word
        assert phone2 in word
        assert word2 is word

    def test_solo_exceptions(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        YourWord, YourPhone = custom_classes(["YourWord", "YourPhone"])
        word = MyWord((0, 10, "a"))
        phone = YourPhone((0,5,"A"))

        with pytest.raises(ValueError):
            word += phone

        with pytest.raises(ValueError):
            word.append(phone)


class TestSequenceInTier:
    
    def test_no_tiergroup(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))

        phone1 = MyPhone((0,5,"A"))
        phone2 = MyPhone((5,10,"AA"))
        phone3 = MyPhone((10,15,"B"))
        phone4 = MyPhone((15,20,"BB"))

        word_tier = SequenceTier([word1, word2])
        phone_tier = SequenceTier([phone2])

        word1.append(phone2)
        word1.append(phone1)
        word2.append(phone3)
        word2.append(phone4)

        assert phone1 in word1
        assert not phone1 in phone_tier

        assert phone1.within.fol.first is phone3

    def test_tiergroup(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))

        phone1 = MyPhone((0,5,"A"))
        phone2 = MyPhone((5,10,"AA"))
        phone3 = MyPhone((10,15,"B"))
        phone4 = MyPhone((15,20,"BB"))

        word_tier = SequenceTier([word1, word2])
        phone_tier = SequenceTier(entry_class=MyPhone)

        # relating tiers should percolate sequence appends
        tier_group = TierGroup([word_tier, phone_tier])
        word1.append(phone1)

        assert phone1 in word1
        assert phone1 in phone_tier

        assert phone1.intier is phone_tier


class TestTiers:
    
    def test_sequence_tier_add(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))

        word_tier1 = SequenceTier([word1])
        word_tier2 = SequenceTier([word2])

        word_tier_copy = word_tier1

        # add breaks reference
        word_tier1 += word_tier2

        assert not word_tier_copy is word_tier1

        for word in [word1, word2]:
            assert word in word_tier1
            assert word.intier is word_tier1
            assert not word.intier is word_tier_copy
            assert not word.intier is word_tier2

    def test_sequence_tier_add_casting(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        class MyWordSub(MyWord):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        word1 = MyWord((0,10,"a"))
        sub_word = MyWordSub((10,20,"b"))
        seq_1 = SequenceInterval((20, 30, "c"))

        word_tier = SequenceTier([word1])

        assert issubclass(MyWordSub, MyWord)

        word_tier += SequenceTier([sub_word])
        assert sub_word in word_tier
        assert sub_word.entry_class is MyWord

        word_tier += SequenceTier([seq_1])
        assert seq_1 in word_tier
        assert seq_1.entry_class is MyWord

    def test_sequence_tier_add_exception(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))

        phone1 = MyPhone((0,5, "AA"))

        word_tier1 = SequenceTier(entry_class=MyWord)

        with pytest.raises(ValueError):
            word_tier1 += word1

        with pytest.raises(ValueError):
            phone_tier = SequenceTier([phone1])
            word_tier1 += phone_tier

    def test_sequence_tier_append(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))

        word_tier1 = SequenceTier(entry_class=MyWord)

        # append does not break reference
        word_tier_copy = word_tier1

        word_tier1.append(word1)
        word_tier1.append(word2)

        assert word_tier_copy is word_tier1
        for word in [word1, word2]:
            assert word in word_tier1
            assert word.intier is word_tier1

        assert word1.fol is word2

    def test_sequence_tier_intg_append(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))
        word3 = MyWord((20,30,"c"))
        phone1 = MyPhone((0,10,"A"))
        phone2 = MyPhone((10,15,"B"))
        phone3 = MyPhone((20, 30, "C"))

        word2.append(phone2)
        word3.append(phone3)

        word_tier = SequenceTier([word1])
        phone_tier = SequenceTier([phone1])

        tier_group = TierGroup([word_tier, phone_tier])

        assert not phone2 in phone_tier
        word_tier.append(word2)
        assert phone2 in phone_tier

        assert not word3 in word_tier
        phone_tier.append(phone3)
        assert word3 in word_tier


    def test_sequence_tier_append_casting(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        class MyWordSub(MyWord):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        word1 = MyWord((0,10,"a"))
        sub_word = MyWordSub((10,20,"b"))
        seq_1 = SequenceInterval((20, 30, "c"))

        word_tier = SequenceTier([word1])
        
        word_tier.append(sub_word)
        assert sub_word in word_tier
        assert sub_word.entry_class is MyWord

        word_tier.append(seq_1)        
        assert seq_1 in word_tier
        assert seq_1.entry_class is MyWord

    def test_sequence_tier_append_exception(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))
        phone1 = MyPhone((0,5,"A"))

        seq_1 = SequenceInterval((0,5,"A"))

        word_tier1 = SequenceTier(entry_class=MyWord)
        word_tier2 = SequenceTier([word1])

        with pytest.raises(ValueError):
            word_tier1.append(phone1)

        with pytest.raises(ValueError):
            word_tier1.append(word_tier2)

    def test_sequence_tier_concat(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((0,10,"b"))

        word_tier1 = SequenceTier([word1])
        word_tier2 = SequenceTier([word2])

        word_tier1.concat(word_tier2)

        assert word1 in word_tier1
        assert word2 in word_tier2

        assert word_tier1.ends.max() == 20
    
    def test_point_tier_add(self):
        MyPoint, = custom_classes(["MyPoint"], points=[0])
        point1 = MyPoint((0,"a"))
        point2 = MyPoint((1, "b"))
        point_tier1 = SequencePointTier([point1])
        point_tier2 = SequencePointTier([point2])

        point_tier_copy = point_tier1
        
        point_tier1 += point_tier2

        assert not point_tier_copy is point_tier1

        point1 in point_tier1
        point2 in point_tier2

    def test_point_tier_append(self):
        MyPoint, = custom_classes(["MyPoint"], points=[0])
        point1 = MyPoint((0,"a"))
        point2 = MyPoint((1, "b"))

        point_tier = SequencePointTier(entry_class=MyPoint)

        point_tier_copy = point_tier

        point_tier.append(point1)
        point_tier.append(point2)

        assert point_tier_copy is point_tier
        assert point1 in point_tier
        assert point2 in point_tier


class TestTierGroups:
    def test_tier_group_append(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))
        phone1 = MyPhone((0,5,"A"))
        phone2 = MyPhone((5,10,"AA"))
        phone3 = MyPhone((10, 15, "B"))
        phone4 = MyPhone((15, 20, "BB"))

        word_tier1 = SequenceTier([word1])
        phone_tier1 = SequenceTier([phone1, phone2])

        word_tier2 = SequenceTier([word2])
        phone_tier2 = SequenceTier([phone3, phone4])


        tier_group1 = TierGroup([word_tier1])
        tier_group1.append(phone_tier1)

        assert phone_tier1 in tier_group1
        assert phone_tier1.within_index == 1

        assert phone1 in word1

        tier_group2 = TierGroup([phone_tier2])
        tier_group2.append(word_tier2)

        assert word_tier2 in tier_group2
        assert word_tier2.within_index == 0
        assert phone3 in word2
        
    def test_tier_group_add(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((10,20,"b"))
        phone1 = MyPhone((0,5,"A"))
        phone2 = MyPhone((5,10,"AA"))
        phone3 = MyPhone((10, 15, "B"))
        phone4 = MyPhone((15, 20, "BB"))

        word_tier1 = SequenceTier([word1])
        phone_tier1 = SequenceTier([phone1, phone2])

        word_tier2 = SequenceTier([word2])
        phone_tier2 = SequenceTier([phone3, phone4])


        tier_group1 = TierGroup([word_tier1, phone_tier1])
        tier_group2 = TierGroup([word_tier2, phone_tier2])

        tier_group1 += tier_group2

        for word in [word1, word2]:
            assert word in tier_group1.MyWord
        for phone in [phone1, phone2, phone3, phone4]:
            assert phone in tier_group1.MyPhone

        assert word1.fol is word2
    
    def test_tier_group_concat(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,10,"a"))
        word2 = MyWord((0,10,"b"))
        phone1 = MyPhone((0,5,"A"))
        phone2 = MyPhone((5,10,"AA"))
        phone3 = MyPhone((0, 5, "B"))
        phone4 = MyPhone((5, 10, "BB"))

        word_tier1 = SequenceTier([word1])
        phone_tier1 = SequenceTier([phone1, phone2])

        word_tier2 = SequenceTier([word2])
        phone_tier2 = SequenceTier([phone3, phone4])


        tier_group1 = TierGroup([word_tier1, phone_tier1])
        tier_group2 = TierGroup([word_tier2, phone_tier2])

        tier_group1.concat(tier_group2)

        assert tier_group1.xmax == 20
        for word in [word1, word2]:
            assert word in tier_group1.MyWord
        for phone in [phone1, phone2, phone3, phone4]:
            assert phone in tier_group1.MyPhone

        assert word1.fol is word2


class TestCleanups:
    def test_sequence_cleanup(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,20,"a"))
        phone1 = MyPhone((2,5,"A"))
        phone2 = MyPhone((10,15,"AA"))

        word1.append(phone1)
        word1.append(phone2)

        assert len(word1)==2

        word1.cleanup()
        assert len(word1)==5
        assert word1.first.label == ""
        assert word1.last.label == ""
        assert phone1.within_index == 1

    def test_tier_cleanups(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((0,15,"a"))
        word2 = MyWord((20,25,"b"))

        word_tier = SequenceTier([word1, word2])
        assert len(word_tier) == 2

        word_tier.cleanup()
        assert len(word_tier) == 3

    def test_tier_group_cleanups(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((2,15,"a"))
        word2 = MyWord((20,25,"b"))
        phone1 = MyPhone((2,5,"A"))
        phone2 = MyPhone((20,22,"BB"))

        tier_group = TierGroup(
            [
                SequenceTier([word1, word2]),
                SequenceTier([phone1, phone2])
            ]
        )

        for tier in tier_group:
            assert len(tier) == 2
        tier_group.cleanup()
        for tier in tier_group:
            assert len(tier) > 2

        assert len(word1) == 2
        assert len(word2) == 2

        starts = np.array([tier.xmin for tier in tier_group])
        ends = np.array([tier.xmax for tier in tier_group])
        assert np.allclose(*starts)
        assert np.allclose(*ends)

    def test_up_copy(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        phone1 = MyPhone((0,5,"A"))

        tier_group = TierGroup([
            SequenceTier(entry_class=MyWord),
            SequenceTier([phone1])
        ])

        assert len(tier_group.MyWord) == 0
        
        tier_group.cleanup()

        assert len(tier_group.MyWord) == 1

        assert phone1 in tier_group.MyWord.first

    
    def test_atg_cleanup(self):
        MyWord, MyPhone = custom_classes(["MyWord", "MyPhone"])
        word1 = MyWord((2,15,"a"))
        word2 = MyWord((20,25,"b"))
        word3 = MyWord((0,15,"a"))
        word4 = MyWord((20,22,"b"))        
        phone1 = MyPhone((2,5,"A"))
        phone2 = MyPhone((20,25,"BB"))     
        phone3 = MyPhone((2,5,"A"))
        phone4 = MyPhone((20,22,"BB"))     

        tg1 = TierGroup([
            SequenceTier([word1, word2]),
            SequenceTier([phone1, phone2])
        ])

        tg2 = TierGroup([
            SequenceTier([word3, word4]),
            SequenceTier([phone3, phone4])
        ])

        atg = AlignedTextGrid()        
        atg.append(tg1)
        atg.append(tg2)

        assert tg1.xmin != tg2.xmin
        assert tg1.xmax != tg2.xmax

        atg.cleanup()

        assert tg1 in atg
        assert tg2 in atg
        
        assert tg1.xmin == tg2.xmin
        assert tg1.xmax == tg2.xmax

        xmins = [tg.xmin for tg in atg]
        xmaxes = [tg.xmax for tg in atg]

        atg.cleanup()
        xmins2 = [tg.xmin for tg in atg]
        xmaxes2 = [tg.xmax for tg in atg]

        for orig, new in zip(xmins, xmins2):
            orig == new
        
        for orig, new in zip(xmaxes, xmaxes2):
            orig == new


        pass


    pass