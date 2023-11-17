class WithinMixins:

    @property
    def within(self):
        if hasattr(self, "_within"):
            return self._within
        return None
    
    @within.setter
    def within(self, obj):
        self._within = obj            

    @property
    def contains(self):
        if hasattr(self, "_contains"):
            return self._contains
        return []
    
    @contains.setter
    def contains(self, new_contains: list):
        self._contains = new_contains
        for item in self._contains:
            if not hasattr(item, "_within"):
                item.within = self
            if not item._within is self:
                item.within = self
            

    @property
    def within_index(self):
        if hasattr(self, "_within") and hasattr(self.within, "_contains"):
            return self.contains.index(self)
        