#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re, xml.etree.ElementTree as ET, io
from collections import defaultdict
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

def extract_coords(lng, lat, country_ranges):
    lng, lat = float(lng), float(lat)
    return country_ranges[0] <= lng <= country_ranges[1] and country_ranges[2] <= lat <= country_ranges[3]

def count_files(country):
    path = os.path.join(WIKI_BASE, country)
    if not os.path.isdir(path):
        return 0
    count = 0
    for root, dirs, files in os.walk(path):
        count += len([f for f in files if f.endswith('.md')])
    return count

def count_kml_pois(country_ranges):
    count = 0
    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        for pm in root.findall('.//kml:Placemark', ns):
            ce = pm.find('.//kml:coordinates', ns)
            if ce is not None and ce.text:
                try:
                    parts = ce.text.strip().split(',')
                    if extract_coords(parts[0], parts[1], country_ranges):
                        count += 1
                except:
                    pass
    except:
        pass
    return count

countries = {
    '泰國': (97, 106, 6, 21),
    '韓國': (125, 130, 33, 44)
}

for country, ranges in countries.items():
    kml_count = count_kml_pois(ranges)
    wiki_count = count_files(country)
    print(f"{country}: KML={kml_count}, Wiki={wiki_count}")
