"""Data format converters module."""
import csv
import json
import logging
import sys
from collections import defaultdict

try:
    import bson
    from bson.json_util import dumps
    HAS_BSON = True
except ImportError:
    HAS_BSON = False
    bson = None
    dumps = None

try:
    import lxml.etree as etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    etree = None

PREFIX_STRIP = False
PREFIX = ""


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
            #            print(dir(dc))
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


def xml_to_jsonl_new(
        source, output, _tagname=None, _prefix_strip=True, dolog=True,
        _encoding='utf8'):
    """Convert XML to JSONL format."""
    try:
        import xmltodict
    except ImportError:
        raise ImportError(
            "xmltodict is required for xml_to_jsonl_new. "
            "Install it with: pip install xmltodict"
        )
    global n
    n = 0

    def handle_obj(_, object):
        global n
        n += 1
        if n % 100 == 0 and dolog:
            logging.info('Converted %d record from xml to jsonl', n)
        output.write(json.dumps(object, ensure_ascii=False))
        output.write('\n')
        return True

    xmltodict.parse(source, item_depth=2, item_callback=handle_obj)


def xml_to_jsonl(
        source, output, tagname, prefix_strip=True, dolog=True,
        _encoding='utf8'):
    """Convert XML to JSONL format using iterparse."""
    if not HAS_LXML:
        raise ImportError(
            "lxml is required for xml_to_jsonl. "
            "Install it with: pip install lxml"
        )
    n = 0
    for event, elem in etree.iterparse(source, recover=True):
        shorttag = elem.tag.rsplit('}', 1)[-1]
        if shorttag == tagname:
            n += 1
            if n % 10000 == 0 and dolog:
                logging.info('Converted %d record from xml to jsonl', n)
            if prefix_strip:
                j = etree_to_dict(elem, prefix_strip)
            else:
                j = etree_to_dict(elem)
            json.dump(j, output, ensure_ascii=False)
            output.write('\n')
            elem.clear()


#        else:
#            logging.debug('Tag: "%s" found instead of %s', elem.tag, tagname)

def csv_to_bson(source, output, delimiter=','):
    """Convert CSV to BSON format."""
    if not HAS_BSON:
        raise ImportError(
            "bson is required for csv_to_bson. "
            "Install it with: pip install pymongo"
        )
    reader = csv.DictReader(source, delimiter=delimiter)
    for j in reader:
        rec = bson.BSON.encode(j)
        output.write(rec)


def csv_to_json(source, output, delimiter=',', quotechar='"'):
    """Convert CSV to JSON format."""
    reader = csv.DictReader(source, delimiter=delimiter, quotechar=quotechar)
    for j in reader:
        output.write(json.dumps(j, ensure_ascii=False))  # .encode('utf8'))
        output.write('\n')  # .encode('utf8'))


def xls_to_json(source, output, keys, start_page=0, start_line=0):
    """Convert XLS to JSON format."""
    sheet = source.sheet_by_index(start_page)
    for rownum in range(start_line, sheet.nrows):
        tmp = []
        for i in range(0, sheet.ncols):
            tmp.append(sheet.row_values(rownum)[i])
        l = json.dumps(dict(zip(keys, tmp)))
        output.write(l.encode('utf8'))
        output.write('\n'.encode('utf8'))


def xlsx_to_json(source, output, keys, _start_page=0, start_line=0):
    """Convert XLSX to JSON format."""
    sheet = source.active  # FIXME! Use start_page instead
    n = 0
    for row in sheet.iter_rows():
        n += 1
        if n < start_line: continue
        tmp = []
        for cell in row:
            tmp.append(cell.value)

        #        l = json.dumps(dict(zip(keys, tmp)), ensure_ascii=False)
        l = dumps(dict(zip(keys, tmp)), ensure_ascii=False)
        output.write(l.encode('utf8'))
        output.write('\n'.encode('utf8'))


def xls_to_bson(source, outputbson, keys, start_page=0, start_line=0):
    """Convert XLS to BSON format."""
    if not HAS_BSON:
        raise ImportError(
            "bson is required for xls_to_bson. "
            "Install it with: pip install pymongo"
        )
    sheet = source.sheet_by_index(start_page)
    for rownum in range(start_line, sheet.nrows):
        tmp = []
        for i in range(0, sheet.ncols):
            tmp.append(sheet.row_values(rownum)[i])
            outputbson.write(bson.BSON.encode(dict(zip(keys, tmp))))


if __name__ == '__main__':
    xml_to_jsonl(sys.argv[1], sys.argv[2], sys.argv[3])
