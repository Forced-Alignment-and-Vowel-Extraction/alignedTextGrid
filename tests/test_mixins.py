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

    class Delta(WithinMixins):
        def __init__(self):
            pass

    def test_contains(self):
        this_a = self.Alpha()
        this_b = self.Beta()

        assert len(this_b.contains) == 0

        this_b.contains = [this_a]

        assert len(this_b.contains) == 1
        assert this_a.within is this_b

        assert this_a.within_index == 0

    def test_path(self):
        this_a1 = self.Alpha()
        this_b1 = self.Beta()
        this_b2 = self.Beta()
        this_d1 = self.Delta()
        this_d2 = self.Delta()

        this_a1.contains = [this_b1, this_b2]
        this_b1.contains = [this_d1]
        this_b2.contains = [this_d2]

        d1_path = this_d1.within_path
        d2_path = this_d2.within_path

        assert len(d1_path) == 2
        for x,y in zip(d1_path, [0,0]):
            assert x==y

        for x,y in zip(d2_path, [1,0]):
            assert x==y

        assert len(this_b2.within_path) == 1
    
    def test_id(self):
        this_a1 = self.Alpha()
        this_b1 = self.Beta()
        this_b2 = self.Beta()
        this_d1 = self.Delta()
        this_d2 = self.Delta()

        this_a1.contains = [this_b1, this_b2]
        this_b1.contains = [this_d1]
        this_b2.contains = [this_d2]

        assert this_d1.id == "0-0"
        assert this_d2.id == "1-0"