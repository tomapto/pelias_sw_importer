

# Pelias sw importer

[![Greenkeeper badge](https://badges.greenkeeper.io/tomapto/pelias_sw_importer.svg)](https://greenkeeper.io/)


## Overview

sw importer用于对四维数据进行处理并按照elasticsearch要求的数据规格进行格式转换，然后倒入到elasticsearch中。

## Prerequisites

* NodeJS `4.0.0` 以上
* Elasticsearch 2.3以上

## 部署方法


```bash
$ git clone https://github.com/tomapto/pelias_sw_importer.git && cd pelias_sw_importer;
$ npm install
```

## 数据准备

标准四维数据，按省名或城市名存储，其中的各个要素对应文件名以其省名或城市名结尾，比如：BLheilongjiang.shp

## 相关配置

默认的配置文件为`~/pelias.json` ，也可以在运行时通过PELIAS_CONFIG来指定pelias.json的位置

sw数据导入工具对应的模块如下所示:

```javascript
    "sw": {
            "datapath": "/mnt1/data/heilongjiang/"
        }
```
其中datapath参数用于指定四维数据的存储路径

## 运行方法


```bash
$ PELIAS_CONFIG=<path_to_config_json> npm start
```

## 导入效率

导入黑龙江省的poi，路网数据84万条，花费12分钟

## 四维数据转换工具实现原理
该转换工具通过python实现，位于sw2json/sw2json.py<br>
单独执行sw2json的方法为：python sw2json.py /mnt/data/heilongjiang heilongjiang<br>
其中/mnt/data/heilongjiang为四维黑龙江数据的存储路径, heilongjiang为要转换的四维数据的省名或城市名<br>

###poi数据转换所需文件及字段
index/POIheilongjiang.shp ：DISPLAY_X, DISPLAY_Y, ADMINCODE, POI_ID<br>
other/PNameheilongjiang.dbf ：FEATID, NAMETYPE, LANGUAGE, NAME<br>
road/R_Nameheilongjiang.dbf ：ROUTE_ID, PATHNAME, LANGUAGE, <br>
road/Rheilongjiang.shp：ID<br>
road/R_LNameheilongjiang.dbf ：ID, ROUTE_ID<br>

