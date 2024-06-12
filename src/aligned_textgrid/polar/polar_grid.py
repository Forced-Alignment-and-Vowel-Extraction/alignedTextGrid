from aligned_textgrid.aligned_textgrid import AlignedTextGrid
from aligned_textgrid.polar.polar_classes import PrStr, ToBI, \
    TurningPoints, Ranges, Levels, Misc
from aligned_textgrid.sequences.word_and_phone import Word, Phone
from praatio import textgrid

class PolarGrid(AlignedTextGrid):
    """Read and structure a PoLaR annotation texgrid

    Either pass a `praatio.textgrid` object, or a path to a textgrid
    file

    Each tier will be accessible by its entr class name. For example, the 
    Levels tier will be accessible with

    ```python
    ptg.Levels
    ```

    Args:
        textgrid (praatio.textgrid): A `praatio.textgrid`
        textgrid_path (str): Path to textgrid file
        entry_classes (list): Appropriately nested entry classes
    """    
    def __init__(self,
                 textgrid: textgrid = None,
                 textgrid_path: str =  None,
                 entry_classes:list = None):

        super().__init__(
            textgrid=textgrid, 
            textgrid_path=textgrid_path, 
            entry_classes=entry_classes
            )
        self._set_named_accessors()
        self._relate_levels_and_ranges()
        self._relate_levels_and_points()
        self._name_groups()
        self._set_group_names()
                
    def _set_named_accessors(self):
        for tg in self.tier_groups:
            for tier in tg:
                setattr(self, tier.entry_class.__name__, tier)

    def _relate_levels_and_ranges(self):
        if self.Levels and self.Ranges:
            for l in self.Levels:
                l.set_ranges_tier(self.Ranges)
                l.set_range_interval()

    def _relate_levels_and_points(self):
        for l in self.Levels:
            l.set_turning_point(self.TurningPoints)
    
    def _name_groups(self):
        wp_classes = [Word, Phone]
        p_classes = [
            PrStr, 
            ToBI, 
            TurningPoints, 
            Ranges, 
            Levels, 
            Misc
        ]
        range_class = [Ranges]

        for group in self:
            entry_classes = group.entry_classes
            if any([issubclass(cl, ecl) for cl in entry_classes for ecl in wp_classes]):
                print("yes")
                group.name = "Word_Phone"
            if any([issubclass(cl, ecl) for cl in entry_classes for ecl in p_classes]):
                group.name = "Points"
            if any([issubclass(cl, ecl) for cl in entry_classes for ecl in range_class]):
                group.name = "RangesTier"


