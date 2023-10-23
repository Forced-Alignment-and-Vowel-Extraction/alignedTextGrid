
class TierGroupMixins:

    def __contains__(self, item):
        return item in self.tier_list
    
    def __getitem__(
            self,
            idx: int|list
    ):
        if type(idx) is int:
            return self.tier_list[idx]
        if len(idx) != len(self):
            raise Exception("Attempt to index with incompatible list")
        if type(idx) is list:
            out_list = []
            for x, tier in zip(idx, self.tier_list):
                out_list.append(tier[x])
            return(out_list)
    
    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self.tier_list)

    def __next__(self):
        if self._idx < len(self.tier_list):
            out = self.tier_list[self._idx]
            self._idx += 1
            return(out)
        raise StopIteration