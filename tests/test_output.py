from aligned_textgrid import AlignedTextGrid, Word, Phone, SequenceTier, TierGroup, custom_classes
from aligned_textgrid.polar.polar_classes import PrStr, ToBI, \
    TurningPoints, Ranges, Levels, Misc
from aligned_textgrid.polar.polar_grid import PolarGrid
from aligned_textgrid.outputs.to_dataframe import to_df
from functools import reduce
import cloudpickle
import tempfile
class TestDataframes:

    atg = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid",
        entry_classes=[Word, Phone]
    )

    entry_classes = [
        [Word, Phone],
        [ToBI, PrStr, TurningPoints, Levels],
        [Ranges]
    ]
    ptg = PolarGrid(
        textgrid_path="tests/test_data/amelia_knew2-basic.TextGrid",
        entry_classes=entry_classes
    )

    def test_interval_df(self):
        df1 = to_df(self.atg[0].Phone[1])
        df2 = to_df(self.atg[0].Phone[1].inword)
        df3 = to_df(self.atg[0].Phone[1].inword, with_subset=False)

        assert df1.shape[0] == 1
        assert df2.shape[0] == len(self.atg[0].Phone[1].inword)
        assert df3.shape[0] == 1

        assert df2.shape[1] == df1.shape[1]*2


    def test_point_df(self):
        df = to_df(self.ptg.PrStr[0])
        assert df.shape[0] == 1

    def test_stier_df(self):
        df1 = to_df(self.atg[0].Phone)
        df2 = to_df(self.atg[0].Word)
        df3 = to_df(self.atg[0].Word, with_subset=False)

        assert df1.shape[0] == len(self.atg[0].Phone)
        assert df2.shape[0] == len(self.atg[0].Phone)
        assert df3.shape[0] == len(self.atg[0].Word)

    def test_ptier_df(self):
        df = to_df(self.ptg.PrStr)

        assert df.shape[0] == len(self.ptg.PrStr)

    def test_tgr_df(self):
        df1 = to_df(self.atg[0])
        df2 = to_df(self.atg[0], with_subset=False)
        
        assert df1.shape[0] == len(self.atg[0].Phone)
        assert df2.shape[0] == len(self.atg[0].Phone) + len(self.atg[0].Word)

    def test_pg_df(self):
        df = to_df(self.ptg[1])
        all_lens = [len(x) for x in self.ptg[1]]
        total_len = reduce(lambda a, b: a+b, all_lens)

        assert df.shape[0] == total_len

    def test_tg_df(self):
        df1 = to_df(self.atg)
        df2 = to_df(self.atg, with_subset=False)

        all_lens = [len(x) for x in self.atg[0]] + [len(x) for x in self.atg[1]]
        total_len = reduce(lambda a, b: a+b, all_lens)

        assert df1.shape[0] == len(self.atg[0].Phone)+ len(self.atg[1].Phone)
        assert df2.shape[0] == total_len

class TestPickle:
    atg = AlignedTextGrid(
        textgrid_path="tests/test_data/KY25A_1.TextGrid",
        entry_classes=[Word, Phone]
    )
    def test_pickling(self):
        assert cloudpickle.loads(cloudpickle.dumps(self.atg))

class TestCustomWrite:

    def test_write(self):
        Transcript, = custom_classes(["Transcript"])
        the_dog = Transcript((0, 10, "the dog"))
        the_cat = Transcript((10, 25, "dog cat"))
        speaker1 = TierGroup([SequenceTier(entry_class=Transcript)])
        speaker2 = TierGroup([SequenceTier(entry_class=Transcript)])

        speaker1[0].append(the_dog)
        speaker2[0].append(the_cat)
        atg = AlignedTextGrid([speaker1, speaker2])
        tmp_file = tempfile.TemporaryFile()
        atg.save_textgrid(tmp_file.name)


        # for phone in [DH, AH0]:
        #     the.append(phone)

        # for phone in [D, AO1, G]:
        #     dog.append(phone)        

        # tier_group = TierGroup([
        #     SequenceTier(entry_class=Word),
        #     SequenceTier(entry_class=Phone)
        # ])

        # tier_group.Word.append(the)
        # tier_group.Word.append(dog)

        # atg = AlignedTextGrid([tier_group])

        

