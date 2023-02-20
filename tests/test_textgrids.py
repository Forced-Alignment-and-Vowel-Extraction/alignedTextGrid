from fave_recode.textgrid_process import processTextGrid
import pytest

tiername_dicts = {
    "no_phone_word": "Style",
    "only_word" : "words",
    "only_phone": "phones",
    "name_word" : "X - words",
    "phone_word" : "X - phones"
}


class TestTierNameProcess:
    def test_all_two(self):
        splits = [processTextGrid.splitTierInfo(tiername_dicts[x]) for x in tiername_dicts]
        split_len = [len(x) for x in splits]
        split_is_two = [x == 2 for x in split_len]
        assert all(split_is_two)

    def test_no_phone_word(self):
        no_phone_word_split = processTextGrid.splitTierInfo(tiername_dicts["no_phone_word"])
        assert no_phone_word_split[0] is None and no_phone_word_split[1] is None

    def test_second_is_wp(self):
        wp_keys = [x for x in tiername_dicts if "words" in x or "phones" in x] 
        splits = [processTextGrid.splitTierInfo(tiername_dicts[x]) for x in wp_keys]
        splits_second = [x[1] for x in splits]
        second_is_wp = [x == "words" or x == "phones" for x in splits_second]
        assert all(second_is_wp)