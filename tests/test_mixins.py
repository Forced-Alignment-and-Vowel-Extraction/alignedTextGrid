from aligned_textgrid.mixins.within import WithinMixins

class TestWithin:

    class Alpha(WithinMixins):
        def __init__(self):
            pass

    class Beta(WithinMixins):
        def __init__(self):
            pass        

    def test_within(self):
        this_a = self.Alpha()
        a_list = [this_a]

        assert not this_a.within
        
        this_a.within = a_list

        assert type(this_a.within) is list
        assert this_a in this_a.within

class TestContains:

    class Alpha(WithinMixins):
        def __init__(self):
            pass

    class Beta(WithinMixins):
        def __init__(self):
            pass

    def test_contains(self):
        this_a = self.Alpha()
        this_b = self.Beta()

        assert len(this_b.contains) == 0

        this_b.contains = [this_a]

        assert len(this_b.contains) == 1
        assert this_a.within is this_b

