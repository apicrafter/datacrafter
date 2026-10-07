"""XML element conversion helpers."""
from collections import defaultdict

try:
    import lxml.etree as etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    etree = None


def etree_to_dict(t, prefix_strip=True):
    """Convert XML etree element to dictionary."""
    if not HAS_LXML:
        raise ImportError(
            "lxml is required for etree_to_dict. "
            "Install it with: pip install lxml"
        )
    tag = t.tag if not prefix_strip else t.tag.rsplit('}', 1)[-1]
    d = {tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                if prefix_strip:
                    k = k.rsplit('}', 1)[-1]
                dd[k].append(v)
        d = {tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[tag].update(('@' + k.rsplit('}', 1)[-1], v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            tag = tag.rsplit('}', 1)[-1]
            if text:
                d[tag]['#text'] = text
        else:
            d[tag] = text
    return d
