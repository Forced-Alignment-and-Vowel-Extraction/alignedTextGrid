from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from alignedTextGrid.sequences.sequences import SequenceInterval
import numpy as np

class Phone(SequenceInterval):
    def __init__(self, Interval = Interval(None, None, None), focus = True):
         super().__init__(Interval, focus)
         self.set_word = super().set_super_instance
         self.set_superset_class(Word)
         self.set_subset_class(Bottom)

    @property
    def inword(self):
        return self.super_instance

class Word(SequenceInterval):
    def __init__(
            self, 
            Interval = Interval(None, None, None), 
            focus = True
        ):
        super().__init__(Interval, focus)
        self.set_phones = super().set_subset_list
        self.set_superset_class(Top)
        self.set_subset_class(Phone)
    
    @property
    def phone_list(self):
        return self.subset_list
    
    @property
    def phones(self):
        return [p.label for p in self.phone_list]

def crunchTiers(phoneTier, wordTier):
    """
    Process phone and word tiers into a wordlist
    """

    if not isinstance(phoneTier, IntervalTier):
        raise Exception("phoneTier must be an instance of IntervalTier")
    if not isinstance(wordTier, IntervalTier):
        raise Exception("wordTier must be an instance of IntervalTier")
    
    word_entries = wordTier.entries
    phones_entries = phoneTier.entries

    word_starts = np.array([x.start for x in word_entries])
    word_ends = np.array([x.end for x in word_entries])
    phone_starts = np.array([x.start for x in phones_entries])
    phone_ends = np.array([x.end for x in phones_entries])

    starts = np.searchsorted(phone_starts, word_starts, side = "left")
    ends = np.searchsorted(phone_ends, word_ends, side = "right")

    tg_phone_seq = [phones_entries[starts[idx]:ends[idx]] for idx,_ in enumerate(word_entries)]
    phone_parts = [[Phone(phone) for phone in sublist] for sublist in tg_phone_seq]

    word_list = []

    for w, ps in zip(word_entries, phone_parts):
        plist = [Phone(p) for p in ps]
        for p in plist:
            p.set_superset_class(Word())
        thisw = Word(w)
        thisw.set_subset_class(Phone())
        thisw.set_phones(plist)
        word_list += [thisw]

    for idx, w in enumerate(word_list):
        if idx == 0:
            w.set_initial()
        else:
            w.set_prev(word_list[idx-1])
        if idx == len(word_list)-1:
            w.set_final()
        else:
            w.set_fol(word_list[idx+1])
    return(word_list)