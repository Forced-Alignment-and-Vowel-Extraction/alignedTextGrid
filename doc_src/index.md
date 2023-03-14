# Aligned TextGrid

The alignedTextGrid package provides a python interface for representing and operating on TextGrids produced by forced aligners like [FAVE](https://github.com/JoFrhwld/FAVE) or the [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/). Classes provided by alignedTextGrid represent hierarchical and precedence relationships among data stored in TextGrid formats allowing for simplified and more accessible analysis of aligned speech data. 

## Not another TextGrid implementation
The alignedTextGrid package is not another TextGrid implementation. TextGrids are a plain text data format used chiefly by the Praat software suite. Programmers have implemented interfaces for this data format so that scripting and data wrangling can be done in a user's programming language of choice. These intefaces include [praatio](http://timmahrt.github.io/praatIO/praatio.html) and Kyle Gorman's [textgrid.py](https://github.com/kylebgorman/textgrid). 

What sets alignedTextGrid apart from other implementations of the TextGrid format is an emphasis on the *relationships* among different items represented in the data. Let's explore this using Gorman's `textgrid.py`:

```{python}
from textgrid import TextGrid

tg = TextGrid.fromFile('usage/resources/josef-fruehwald_speaker.TextGrid')
```

In `tg` we now have a representation of our TextGrid. TextGrids are primarily organized into tiers which can store data as either points or intervals. In `textgrid.py` these tiers are accessed by their index, so `tg[0]` is the highest tier, `tg[1]` is the next highest, and so on (our data only has two tiers). These tiers can also have names like in our data:

```{python}
print(f"First tier is named {tg[0].name}")
print(f"Second tier is named {tg[1].name}")
```

In the case of *aligned* TextGrid data like ours, these names are more than a convenience. Tiers on aligned data are *hierarchical*. Both of our tiers represent the same information but at different levels of granularity: the `words` tier represents the data as a series of words and the `phones` tier represents the data as a series of phones. Put another way, the `phones` tier and the `words` tier are codependent. Praat TextGrids, and by extension its Python implementations, are largely agnostic when it comes to the relationship between tiers. This allows them to handle a wide range of use cases, but for *aligned* data, the dependency relationships between tiers are metadata which should be incorporated into the data representations. Through classes like `RelatedTiers`, alignedTextGrid extends these general TextGrid data structures for use with force-aligned data.

### Relating data within and across tiers
Praat TextGrids store time-dependent data, and within a tier each data entry has an ordered relationship to others within its tier. While having the specific time-domain data is useful, often what we are interested in is the abstracted relationship between points like which came first or whether two annotations overlap in time. Python implementations of TextGrids store the time-domain data as part of the representation, but these ordered relationships are represented more abstractly.

```{python}
wordTier = 0

tg[wordTier][0] > tg[wordTier][1]
```

In `textgrid.py`, we can compare two words and get a true or false value. In the example above, the comparison is false: word zero does not occur after word 1. <!-- On an abstract level this ordering as actually kinda confusing. A > B => false which makes sense if you consider time stamps, but if we want to treat > and < as *precedence* operators rather than comparitors, the truth table needs flipped. (1) we might want to do that (2) we might want to document that behavior. -CB 13 March 2023 -->

A major issue when working with these precedence orderings is knowing and remembering where in the data you are. In the following example, we use the `random` library to choose an arbitrary entry in the word tier. We do not store the index of this piece of data, so how do we know its relationship to other pieces of data? What word comes after it or before it? How would we get to them? In this case, we could use the `.index()` method to search the original list for the item we have. This works well, but it is costly because the whole data set needs to be searched. For a short passage like we're using, that is not a major problem, but when working with hours-long audio recordings, searches like that can slow down an analysis or data coding script.

```{python}
from random import randint
num_words = len(tg[wordTier])

word = tg[wordTier][randint(0,num_words)]
```

The alignedTextGrid package aims to resolve these issues by incorporating these relationships into the representations from the start. The attribute `.fol` of `alignedTextGrid.SequenceInterval` provides access to the next interval in the sequence even if you don't know precisely where in the sequence you are. You can also use the `.intier` and `.subset_list` attributes to navigate up and down the tier hierarchy.

## Installation
<!-- TODO: documnet other package managers like conda -CB 14 March 2023 -->
To install alignedTextGrid using pip, run the following command in your terminal:

```bash
pip install git+https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/
```

For examples on how to use the pacakge, see the [Usage](usage/) pages.
