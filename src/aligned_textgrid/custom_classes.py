from aligned_textgrid.sequences.sequences import *
from aligned_textgrid.points.points import *
from praatio.utilities.utils import Interval
from typing import Type



def _top_constructor(self):
    Top.__init__(self)

def _bottom_constructor(self):
    Bottom.__init__(self)

def _make_top()->SequenceInterval:

    n_top = len(Top.__subclasses__())
    this_top_name = f"Top_{n_top}"
    this_top = type(
        this_top_name,
        (Top, ), 
        {"__init__": _top_constructor}
    )

    return this_top

def _make_bottom()->SequenceInterval:
    n_bottom = len(Bottom.__subclasses__())
    this_bottom_name = f"Bottom_{n_bottom}"
    this_bottom = type(
        this_bottom_name, 
        (Bottom, ), 
        {"__init__": _bottom_constructor}
    )

    return this_bottom

def custom_classes(
        class_list:list[str] = [],
        return_order: list[str] | list[int] | None = None,
        points:list[int] = []        
) -> list[type[SequenceInterval]|type[SequencePoint]]:
    """Generate custom interval classes

    Passing `custom_classes()` a list of Sequence names wil return a list of
    `SequenceInterval` subclasses with those names. The first name passed to `class_list`
    will be at the top of the hierarchy, the second name will be the subset class of the 
    first, and so on.
    
    Examples:

        To change the order in which the custom classes are *returned*, specify `return_order` 
        with either indices or class names. For example, if you have Words, Syllables, and Phones in
        a hierarchical relationship in a textgrid, you can run the following:


        ```{python}
        from aligned_textgrid import custom_classes

        custom_classes(["Word", "Syllable", "Phone"])
        ```

        But if the order of the textgrid tiers has Word as the bottom tier and Phone as the top, you can specify `return_order`
        like so:

        ```{python}
        custom_classes(
            class_list = ["Word", "Syllable", "Phone"],
            return_order = [2, 1, 0]
            # or
            # return_order = ["Phone", "Syllable", "Word]
        )
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

    this_top = _make_top()
    this_bottom = _make_bottom()

    if return_order is None:
        return_order = class_list

    class_out_list = []
    if type(class_list) is str and len(points) == 0:
        newclass = type(
            class_list, 
            (SequenceInterval, ), 
            dict(SequenceInterval.__dict__)
        )
        newclass.set_superset_class(this_top)
        newclass.set_subset_class(this_bottom)
        return newclass
    
    if type(class_list) is str and len(points) != 0:
        newclass = type(
            class_list, 
            (SequencePoint, ), 
            dict(SequencePoint.__dict__)
        )
        return newclass

    if type(class_list) is list:
        for idx, name in enumerate(class_list):
            if idx in points:
                class_out_list.append(
                    type(name, (SequencePoint,), dict(SequencePoint.__dict__))
                )
            else:
                class_out_list.append(
                    type(name, (SequenceInterval,), dict(SequenceInterval.__dict__))
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

def clone_class(
        entry_class:SequenceInterval|SequencePoint,
        recurse = False
        ) -> SequenceInterval|SequencePoint:
    """Clone an entry class. It will have the same name, but
    any changes to its class properties will not be reflected
    in the original class.

    Args:
        entry_class (SequenceInterval | SequencePoint): 
            A SequenceInterval or SequencePoint to clone
        recurse (bool, optional): 
            Used internally to clone the entire hierarchy. 
            Defaults to False.

    Returns:
        (SequenceInterval|SequencePoint): A cloned entry class
    """
    
    if issubclass(entry_class, SequenceInterval):
        if not issubclass(entry_class.superset_class, Top) \
        and not recurse:
            raise Exception("Entry class to clone must be top of hierarchy")
        
        cloned = type(
                entry_class.__name__, 
                (entry_class, ), 
                dict(entry_class.__dict__)
            )
        
        if issubclass(cloned.superset_class, Top):
            cloned.set_superset_class(
                _make_top()
            )

        if issubclass(cloned.subset_class, Bottom):
            cloned.set_subset_class(
                _make_bottom()
            )

        if (not cloned is cloned.subset_class.superset_class) \
           and issubclass(cloned.subset_class, SequenceInterval):
            new_subset = clone_class(cloned.subset_class, recurse=True)
            cloned.set_subset_class(new_subset)

           
    if issubclass(entry_class, SequencePoint):
        cloned = type(
                entry_class.__name__, 
                (entry_class, ), 
                dict(entry_class.__dict__)
        )
    
    return cloned

def get_class_hierarchy(
        entry_class:SequenceInterval, 
        out_list = []
    )->list[SequenceInterval]:
    """Given a SequenceInterval, this will return
    the entire class hierarchy

    Args:
        entry_class (SequenceInterval): 
            Entry class to search the hierarchy for
        out_list (list, optional): 
            Used internally for recursive search.
            Defaults to [].

    Returns:
        (list[SequenceInterval]):
            The class hierarchy
    """
    if (not issubclass(entry_class.superset_class, Top)) \
       and entry_class.superset_class not in out_list:
        out_list = get_class_hierarchy(entry_class.superset_class, out_list)

    if entry_class not in out_list: 
        out_list.append(entry_class)

    if not issubclass(entry_class.subset_class, Bottom):
        out_list = get_class_hierarchy(entry_class.subset_class, out_list)
    
    return out_list
