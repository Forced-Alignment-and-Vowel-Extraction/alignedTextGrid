from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.points.points import *
from praatio.utilities.utils import Interval
from typing import Type

def custom_classes(
        class_list:list[str] = [],
        return_order: list[str] | list[int] | None = None,
        points:list[int] = []        
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
        points (list[int], optional): 
            Indices of which classes should be points, rather than intervals

    Returns:
        (list[Type[SequenceInterval]]): A list of custom `SequenceInterval` subclasses
    """
    def _sequence_constructor(
            self, 
            Interval = Interval(None, None, None)
        ):
        SequenceInterval.__init__(self, Interval=Interval)
    
    def _point_constructor(
            self,
            Point = Point(0, "")
    ):
        SequencePoint.__init__(self, Point)

    def _top_constructor(self):
        Top.__init__(self)

    def _bottom_constructor(self):
        Bottom.__init__(self)


    n_top = len(Top.__subclasses__())
    n_bottom = len(Bottom.__subclasses__())

    this_top_name = f"Top_{n_top}"
    this_bottom_name = f"Bottom_{n_bottom}"

    this_top = type(
        this_top_name,
        (Top, ), 
        {"__init__": _top_constructor}
    )
    
    this_bottom = type(
        this_bottom_name, 
        (Bottom, ), 
        {"__init__": _bottom_constructor}
    )

    if return_order is None:
        return_order = class_list

    class_out_list = []
    if type(class_list) is str and len(points) == 0:
        newclass = type(
            class_list, 
            (SequenceInterval, ), 
            {"__init__": _sequence_constructor}
        )
        newclass.set_superset_class(this_top)
        newclass.set_subset_class(this_bottom)
        return newclass
    
    if type(class_list) is str and len(points) != 0:
        newclass = type(
            class_list, 
            (SequencePoint, ), 
            {"__init__": _point_constructor}
        )
        return newclass

    if type(class_list) is list:
        for idx, name in enumerate(class_list):
            if idx in points:
                class_out_list.append(
                    type(name, (SequencePoint,), {"__init__": _point_constructor})
                )
            else:
                class_out_list.append(
                    type(name, (SequenceInterval,), {"__init__": _sequence_constructor})
                )
                
        interval_classes = [x 
                            for x in class_out_list 
                            if issubclass(x, SequenceInterval)
                            ]
        for idx, entry in enumerate(interval_classes):
            if idx == 0:
                entry.set_superset_class(this_top)
            if idx == len(interval_classes)-1:
                entry.set_subset_class(this_bottom)
            else:
                entry.set_subset_class(interval_classes[idx+1])

        if type(return_order[0]) is int:
            return_list = [class_out_list[idx] for idx in return_order]
        elif type(return_order[0]) is str:
            return_idx = [return_order.index(x) for x in class_list]
            return_list = [class_out_list[idx] for idx in return_idx] 
        return return_list