from aligned_textgrid.aligned_textgrid import AlignedTextGrid
from praatio import textgrid

class PolarGrid(AlignedTextGrid):
    """_Read and structure a PoLaR annotation texgrid_

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