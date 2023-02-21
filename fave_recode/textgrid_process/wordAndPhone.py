from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier
import numpy as np

class SequenceInterval:
    def __init__(self, Interval = Interval(None, None, None), focus = True):
        self.start = Interval.start
        self.end = Interval.end
        self.label = Interval.label
        if focus:
            self.fol = self.__class__(focus=False)
            self.prev = self.__class__(focus=False)

    def set_fol(self, next_int):
        if isinstance(next_int, self.__class__):
            self.fol = next_int
        elif isinstance(next_int, Interval):
            self.fol = self.__class__(next_int, focus = False)
        else:
            raise Exception(f"Following segment must be an instance of {self.__class__.__name__} or Interval")

    def set_prev(self, prev_int):
        if isinstance(prev_int, self.__class__):
            self.prev = prev_int
        elif isinstance(prev_int, Interval):
            self.prev = self.__class__(prev_int, focus = False)
        else:
            raise Exception(f"Previous segment must be an instance of {self.__class__.__name__} or Interval")
    
    def set_final(self):
        self.set_fol(Interval(None, None, "#"))  

    def set_initial(self):
        self.set_prev(Interval(None, None, "#"))

    def set_feature(self, feature, value):
        setattr(self, feature, value)

    def return_interval(self):
        return Interval(self.start, self.end, self.label)

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