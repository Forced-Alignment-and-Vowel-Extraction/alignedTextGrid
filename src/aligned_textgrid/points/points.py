from praatio.utilities.constants import Point

class PrecedenceMixins:

    def set_fol(
            self, next_int):
        """_Sets the following instance_

        Args:
            next_int (SequenceInterval): 
                Sets the `next_int` as the `fol` interval.
                Must be of the same class as the current object.
                That is, `type(next_int) is type(self)`
        """
        if next_int is self:
            raise Exception(f"A segment can't follow itself.")
        if self.label == "#":
            return
        if self.fol is next_int:
            return
        elif type(next_int) is type(self):
            self.fol = next_int
            self.fol.set_prev(self)
        else:
            raise Exception(f"Following segment must be an instance of {type(self).__name__}")

    def set_prev(self, prev_int):
        """_Sets the previous intance_

        Args:
            prev_int (SequenceInterval):
                Sets the `prev_int` as the `prev` interval
                Must be of the same class as the current object.
                That is, `type(prev_int) is type(self)`                
        """
        if prev_int is self:
            raise Exception("A segment can't precede itself.")
        if self.label == "#":
            return
        if self.prev is prev_int:
            return
        elif type(prev_int) is type(self):
            self.prev = prev_int
            self.prev.set_fol(self)
        else:
            raise Exception(f"Previous segment must be an instance of {type(self).__name__}")
    
    def set_final(self):
        """_Sets the current object as having no `fol` interval_
        
        While `self.fol` is defined for these intervals, the actual
        instance does not appear in `self.super_instance.subset_list`
        """
        self.set_fol(type(self)(Interval(None, None, "#")))  

    def set_initial(self):
        """_Sets the current object as having no `prev` interval_

        While `self.prev` is defined for these intervals, the actual 
        instance does not appear in `self.super_instance.subset_list`
        """
        self.set_prev(type(self)(Interval(None, None, "#")))

class  SeqPoint:
    def __init__(
            self,
            Point
        ):
        if not Point:
            Point = Point(0, 0)
        
        self.time = Point.time
        self.label = Point.label

        self.intier = None
        self.tiername = None
        self.pointspool = None

    def set_intier(self, tier):
        self.intier = tier
    
    def set_tiername(self, tier):
        self.tiername = tier.name

    def set_pointspool(self):
        pass

    def nearest(self):
        pass
        # 
    