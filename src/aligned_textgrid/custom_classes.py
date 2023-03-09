from aligned_textgrid.sequences.sequences import *
from praatio.utilities.utils import Interval
from typing import Type

def custom_classes(
        class_list:list[str] = [],
        return_order: list[str] | list[int] | None = None
) -> list[Type[SequenceInterval]]:
    """_Generate custom interval classes_

    Passing `custom_classes()` a list of Sequence names wil return a list of
    `SequenceInterval` subclasses with those names. The first name passed to `class_list`
    will be at the top of the hierarchy, the second name will be the subset class of the 
    first, and so on.

    To change the order in which the custom classes are *returned*, specify `return_order` 
    with either indices or class names. For example, if you have Words, Syllables, and Phones in
    a hierarchical relationship in a textgrid, you can run the following:

    ```python
    custom_classes(["Word", "Syllable", "Phone"])
    # [alignedTextGrid.custom_classes.Word,
    #  alignedTextGrid.custom_classes.Syllable,
    #  alignedTextGrid.custom_classes.Phone]
    ```

    But if the order of the textgrid tiers has Word as the bottom tier and Phone as the top, you can specify `return_order`
    like so:

    ```python
    custom_classes(
        class_list = ["Word", "Syllable", "Phone"],
        return_order = [2, 1, 0]
        # or
        # return_order = ["Phone", "Syllable", "Word]
    )
    # [alignedTextGrid.custom_classes.Phone,
    #  alignedTextGrid.custom_classes.Syllable,
    #  alignedTextGrid.custom_classes.Word]
    ```

    This way, you can use `custom_classes()` directly as the `entry_classes` argument in `AlignedTextGrid`

    ```python
    AlignedTextGrid(
        textgrid_path = "syllables.TextGrid",
        entry_classes = custom_classes(
            class_list = ["Word", "Syllable", "Phone"],
            return_order = [2, 1, 0]
        )
    )
    ```

    Args:
        class_list (list[str], optional): 
            A list of desired class names, in their hierarchical order. Defaults to [].
        return_order (list[str] | list[int] | None, optional): 
            A return order for the custom classes, if not in hierarchical order. Defaults to None.

    Returns:
        (list[Type[SequenceInterval]]): A list of custom `SequenceInterval` subclasses
    """
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