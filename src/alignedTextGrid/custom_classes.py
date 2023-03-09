from alignedTextGrid.sequences.sequences import *
from praatio.utilities.utils import Interval
from typing import Type

def custom_classes(
        class_list:list[str] = [],
        return_order: list[str] | list[int] | None = None
) -> list[Type[SequenceInterval]]:
    def _constructor(
            self, 
            Interval = Interval(None, None, None)
        ):
        SequenceInterval.__init__(self, Interval=Interval)

    if return_order is None:
        return_order = class_list

    class_out_list = []
    if type(class_list) is str:
        newclass = type(class_list, (SequenceInterval, ), {"__init__": _constructor})
        return newclass
    elif type(class_list) is list:
        for name in class_list:
            class_out_list.append(
                type(name, (SequenceInterval,), {"__init__": _constructor})
            )
        for idx, entry in enumerate(class_out_list):
            if idx == len(class_out_list)-1:
                pass
            else:
                class_out_list[idx].set_subset_class(class_out_list[idx+1])
        if type(return_order[0]) is int:
            return_list = [class_out_list[idx] for idx in return_order]
        elif type(return_order[0]) is str:
            return_idx = [return_order.index(x) for x in class_list]
            return_list = [class_out_list[idx] for idx in return_idx] 
        return return_list