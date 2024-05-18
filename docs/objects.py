import aligned_textgrid
import sphobjinv as soi
from pathlib import Path
inv = soi.Inventory(fname_plain = Path("objects.txt"))

for idx in range(len(inv.objects)):
    obj = inv.objects[idx]
    basename = obj.name.split(".")[-1]
    if hasattr(aligned_textgrid, basename):
        obj_dict = obj.json_dict()
        obj_dict["name"] = "aligned_textgrid." + basename
        new_obj = soi.DataObjStr(**obj_dict)
        inv.objects.append(new_obj)

df = inv.data_file()
dfc = soi.compress(df)
soi.writebytes("objects.inv", dfc)