from typing import Dict, List, Tuple, Union

def splitTierInfo(tierName: str) -> Union[List[str], List[None]]:
    """
    Split textgrid tiers into speaker info.
    """
    if not "words" in tierName and not "phones" in tierName:
        return([None, None])
    else:
        if "-" in tierName:
            out = tierName.split(" - ")
        else:
            out = ["Speaker", tierName]
        return(out)


if __name__ == "__main__":
    pass