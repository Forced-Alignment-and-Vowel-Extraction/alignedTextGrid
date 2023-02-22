from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
from sequences import SequenceInterval
import numpy as np

class Phone(SequenceInterval):
    def __init__(self, Interval = Interval(None, None, None), focus = True):
         super().__init__(Interval, focus)

    def set_word(self, word):
        if isinstance(word, Word):
            self.inword = word

class Word(SequenceInterval):
    def __init__(self, Interval = Interval(None, None, None), PhoneList = [Phone()], focus = True):
        super().__init__(Interval, focus)
        for phone in PhoneList:
            if isinstance(phone, Phone):
                phone.set_word(self)
        self.PhoneList = PhoneList
        for idx, p in enumerate(self.PhoneList):
            if idx == 0:
                p.set_initial()
            else:
                p.set_prev(self.PhoneList[idx-1])
            if idx == len(self.PhoneList)-1:
                p.set_final()
            else:
                p.set_fol(self.PhoneList[idx+1])
    
    @property
    def phones(self):
        return [p.label for p in self.PhoneList]

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
        thisw = Word(w, plist)
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