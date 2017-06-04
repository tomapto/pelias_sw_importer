
# -*- coding: gbk -*-

import os.path
import shapefile
import struct
import datetime
import decimal
import itertools
import json
import sys


def dbfreader(f):
    """Returns an iterator over records in a Xbase DBF file.

    The first row returned contains the field names.
    The second row contains field specs: (type, size, decimal places).
    Subsequent rows contain the data records.
    If a record is marked as deleted, it is skipped.

    File should be opened for binary reads.

    """
    # See DBF format spec at:
    #     http://www.pgts.com.au/download/public/xbase.htm#DBF_STRUCT

    numrec, lenheader = struct.unpack('<xxxxLH22x', f.read(32))
    numfields = (lenheader - 33) // 32

    fields = []
    for fieldno in xrange(numfields):
        name, typ, size, deci = struct.unpack('<11sc4xBB14x', f.read(32))
        name = name.replace('\0', '')  # eliminate NULs from string
        fields.append((name, typ, size, deci))
    yield [field[0] for field in fields]
    yield [tuple(field[1:]) for field in fields]

    terminator = f.read(1)
    assert terminator == '\r'

    fields.insert(0, ('DeletionFlag', 'C', 1, 0))
    fmt = ''.join(['%ds' % fieldinfo[2] for fieldinfo in fields])
    fmtsiz = struct.calcsize(fmt)
    for i in xrange(numrec):
        record = struct.unpack(fmt, f.read(fmtsiz))
        if record[0] != ' ':
            continue  # deleted record
        result = []
        for (name, typ, size, deci), value in itertools.izip(fields, record):
            if name == 'DeletionFlag':
                continue
            if typ == "N":
                value = value.replace('\0', '').lstrip()
                if value == '':
                    value = 0
                elif deci:
                    value = decimal.Decimal(value)
                else:
                    value = int(value)
            elif typ == 'D':
                y, m, d = int(value[:4]), int(value[4:6]), int(value[6:8])
                value = datetime.date(y, m, d)
            elif typ == 'L':
                value = (value in 'YyTt' and 'T') or (value in 'NnFf' and 'F') or '?'
            elif typ == 'F':
                value = float(value)
            result.append(value)
        yield result




def FullToHalf(s):
    n = []
    s = s.decode('utf-8')
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)
    return ''.join(n)


if __name__ == "__main__":
    rootdir = sys.argv[1]
    province = sys.argv[2]
    result = ""


    #parse poi
    poiPath = rootdir + os.path.sep + "index" + os.path.sep + "POI" + province + ".shp"
    poi = shapefile.Reader(poiPath)
    records = poi.records()
    poiId2poiInfo = {}
    featid2name = {}
    featid2street = {}
    featid2streetno = {}

    for record in records:
        poiId = record[7].strip()
        x = record[5].strip()
        y = record[6].strip()
        adcode = record[4].strip()
        poiId2poiInfo[poiId] = (x, y, adcode)

    pnamePath = rootdir + os.path.sep + "other" + os.path.sep + "PName" + province + ".dbf"
    with open(pnamePath, 'rb') as fPName:
        db = list(dbfreader(fPName))
        i = 0
        for record in db:
            if i<2:
                i+=1
                continue
            featid = record[0].strip()
            nameType = record[1].strip()
            language = record[8].strip()
            name = record[2].strip().decode('gbk').encode('utf8')

            if nameType == "9":
                featid2name[(featid, language)] = name
            elif nameType == "18" :
                featid2street[featid] = name
            elif nameType == "19":
                name = FullToHalf(name)
                featid2streetno[featid] = name




    for poiId in poiId2poiInfo.keys():
        x = poiId2poiInfo[poiId][0]
        y = poiId2poiInfo[poiId][1]
        adcode = poiId2poiInfo[poiId][2]
        chnName = featid2name[(poiId, "1")].decode('utf-8')
        pinyin = featid2name[(poiId, "3")].replace("&", "&amp;")

        street = ""
        streetno = ""
        try:
            street = featid2street[poiId]
        except:
            pass

        try:
            streetno = featid2streetno[poiId]
        except:
            pass

        tags = {}
        tags["amenity"] = "theatre"
        tags["name"] = chnName
        tags["name:zh"] = chnName
        tags["addr:street"] = street.decode('utf-8')
        tags["addr:housenumber"] = streetno

        record = {}
        record["id"] = poiId
        record["type"] = "node"
        record["lat"] = y
        record["lon"] = x
        record["tags"] = tags

        strRecord = json.dumps(record, ensure_ascii=False  ) + "\n"
        print strRecord.encode('utf8')



    #parse road
    rnamePath = rootdir + os.path.sep + "road" + os.path.sep + "R_Name" + province + ".dbf"
    rPath = rootdir + os.path.sep + "road" + os.path.sep + "R" + province + ".shp"
    r_lnamePath = rootdir + os.path.sep + "road" + os.path.sep + "R_LName" + province + ".dbf"

    roadId2points = {}
    routeId2chnName = {}
    routeId2pinyin = {}
    id2routeId = {}


    road = shapefile.Reader(rPath)
    shape_records = road.shapeRecords()
    for shape_record in shape_records:
        id = shape_record.record[1].strip()
        roadId2points[id] = shape_record.shape.points


    with open(rnamePath, 'rb') as fRName:
        db = list(dbfreader(fRName))
        i = 0
        for record in db:
            if i<2:
                i+=1
                continue
            routeId = record[0].strip()
            pathname = record[2].strip().decode('gbk').encode('utf8')
            language = record[-2].strip()
            if language == "1":
                routeId2chnName[routeId] = pathname
            elif language == "3":
                routeId2pinyin[routeId] = pathname



    with open(r_lnamePath, 'rb') as fLRName:
        db = list(dbfreader(fLRName))
        i = 0
        for record in db:
            if i<2:
                i+=1
                continue
            id = record[1].strip()
            routeId = record[2].strip()
            id2routeId[id] = routeId

    for roadId in id2routeId.keys():
        tags = {}
        chnName = routeId2chnName[ id2routeId[roadId] ].decode('utf-8')
        tags["name"] = chnName
        tags["addr:street"] = chnName
        tags["area"] = "yes"

        nodes = []
        node = {}
        points = roadId2points[ roadId ]
        centroid = {}
        for point in points:
            node["lat"] = point[1]
            node["lon"] = point[0]
            centroid["lat"] = point[1]
            centroid["lon"] = point[0]
            nodes.append(node)

        record = {}
        record["id"] = roadId
        record["type"] = "way"
        record["nodes"] = nodes
        record["tags"] = tags
        record["centroid"] = centroid

        strRecord = json.dumps(record, ensure_ascii=False) + "\n"
        print strRecord.encode('utf8')





