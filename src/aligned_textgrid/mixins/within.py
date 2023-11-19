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
            return self.within.contains.index(self)
        return None
    
    def _get_within_path(self, obj):
        path = []
        if not obj.within_index is None:
            path += [obj.within_index]
            path += self._get_within_path(obj.within)
            return path
        
        return path

    @property
    def within_path(self):
        path =  self._get_within_path(obj = self)
        path.reverse()
        return path
    
    @property
    def id(self):
        path = self.within_path
        return "-".join([str(x) for x in path])