from collections import defaultdict

def xml_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(xml_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update((k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['text'] = text
        else:
            d[t.tag] = text
    return d

def pluralize_dict_key(d, key):
    """ Given a dictionary, find key and ensure they are 
        represented as lists, regardless of length.
    """
    for k, v in d.items():
        if k == key and not isinstance(v, list):
            d[k] = [v]
        elif isinstance(v, dict):
            d[k] = pluralize_dict_key(v, key)
        elif isinstance(v, list):
            d[k] = [pluralize_dict_key(ld, key) for ld in v if isinstance(ld, dict)]
    return d
