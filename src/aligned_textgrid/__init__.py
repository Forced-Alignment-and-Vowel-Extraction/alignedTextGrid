from aligned_textgrid.sequences.sequences import SequenceInterval, Top, Bottom
from aligned_textgrid.sequences.word_and_phone import Word, Phone
from aligned_textgrid.points.points import SequencePoint
from aligned_textgrid.points.tiers import SequencePointTier, PointsGroup
from aligned_textgrid.sequences.tiers import SequenceTier, TierGroup
from aligned_textgrid.aligned_textgrid import AlignedTextGrid
from aligned_textgrid.sequence_list import SequenceList
from aligned_textgrid.custom_classes import custom_classes
from aligned_textgrid.outputs.to_dataframe import to_df

from importlib.metadata import version

from pathlib import Path
import toml

__version__ = "unknown"
# adopt path to your pyproject.toml
pyproject_toml_file = Path(__file__).parent.parent.parent / "pyproject.toml"
if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
    data = toml.load(pyproject_toml_file)
    # check project.version
    if "tool" in data and "poetry" in data["tool"] and "version" in data["tool"]["poetry"]:
        __version__ = data["tool"]["poetry"]["version"]

__all__ = [
    "SequenceInterval",
    "SequencePoint",
    "PointsGroup",
    "Top",
    "Bottom",
    "Word",
    "Phone",
    "SequenceTier",
    "SequencePointTier",
    "TierGroup",
    "SequenceList",
    "AlignedTextGrid",
    "custom_classes",
    "to_df",
    "__version__"
]