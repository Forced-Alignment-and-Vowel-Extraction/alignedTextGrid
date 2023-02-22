from typing import Dict, List, Tuple, Union

class speakerTiers:
    """
    Given testgrid tiernames, structures their word and phone relationships
    """
    def __init__(self, tierNames):
        self.tierNames = tierNames
        self.splitTierNames = [splitTierInfo(x) for x in tierNames]
        self.tierNames = [" - ".join(x) for x in self.splitTierNames]

    def __iter__(self):
        self._current = 0
        return self

    def __next__(self):
        if self._current >= len(self.speaker_tier_dict):
            raise StopIteration
        else:
            this = list(self.speaker_tier_dict.keys())[self._current]
            self._current += 1
            return(this)
    
    def __getitem__(self, idx):
        return self.speaker_tier_dict[idx]

    @property
    def speakers(self):
        individual_speakers = [x[0] for x in self.splitTierNames if x[0]]
        unique_speakers = set(individual_speakers)
        return(unique_speakers)

    @property
    def speaker_tier_dict(self):
        out = {}
        for speaker in self.speakers:
            out[speaker] = {"phones": None, "words": None}
            for tn in self.tierNames:
                if speaker in tn:
                    if "words" in tn:
                        out[speaker]["words"] = tn
                    if "phones" in tn:
                        out[speaker]["phones"] = tn
        return(out)



def splitTierInfo(tierName: str) -> Union[List[str], List[None]]:
    """
    Split textgrid tiers into speaker info.
    """
    if not "words" in tierName and not "phones" in tierName:
        return([None, None])
    else:
        if "-" in tierName:
            out = tierName.split(" - ")
        else:
            out = ["Speaker", tierName]
        return(out)

if __name__ == "__main__":
    pass