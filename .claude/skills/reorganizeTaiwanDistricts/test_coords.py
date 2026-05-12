#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 載入縣市映射
with open(r'.\.claude\skills\reorganizeTaiwanDistricts\county_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)['mapping']

# 載入 GeoJSON
with open(r'twgeojson\twtown2010.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

test_point = [121.2426817, 25.1154843]

found_county_old = None
for feature in data['features']:
    props = feature['properties']
    county = props.get('county', '?')
    town = props.get('town', '?')

    geom = feature['geometry']
    if geom['type'] == 'MultiPolygon':
        for polygon_ring in geom['coordinates']:
            if polygon_ring:
                coords = polygon_ring[0]
                if coords:
                    lngs = [float(c[0]) for c in coords]
                    lats = [float(c[1]) for c in coords]
                    min_lng, max_lng = min(lngs), max(lngs)
                    min_lat, max_lat = min(lats), max(lats)

                    if min_lng <= test_point[0] <= max_lng and min_lat <= test_point[1] <= max_lat:
                        print(f'✓ 邊界內: {county}/{town}')
                        found_county_old = county
                        break
    if found_county_old:
        break

if found_county_old:
    found_county_new = mapping.get(found_county_old, found_county_old)
    print(f'\n✓ 舊名稱: {found_county_old}')
    print(f'✓ 新名稱: {found_county_new}')
else:
    print('❌ 找不到邊界')
