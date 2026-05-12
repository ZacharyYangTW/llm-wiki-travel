#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re, xml.etree.ElementTree as ET, io
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

WIKI_BASE = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"

THAILAND_COORDS = (97, 106, 6, 21)
KOREA_COORDS = (125, 130, 33, 44)

def extract_pois(ranges, country):
    pois = []
    try:
        tree = ET.parse(KML_FILE)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        for pm in root.findall('.//kml:Placemark', ns):
            ne = pm.find('kml:name', ns)
            ce = pm.find('.//kml:coordinates', ns)
            if ne is not None and ce is not None:
                name = ne.text.strip()
                coords_text = ce.text.strip()
                try:
                    parts = coords_text.split(',')
                    lng, lat = float(parts[0]), float(parts[1])
                    if ranges[0] <= lng <= ranges[1] and ranges[2] <= lat <= ranges[3]:
                        pois.append({'name': name, 'lng': lng, 'lat': lat})
                except:
                    pass
    except:
        pass
    return pois

def get_wiki_names(country):
    names = set()
    path = os.path.join(WIKI_BASE, country)
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('.md'):
                    names.add(f[:-3].lower())
    return names

def sanitize(name):
    name = re.sub(r'[/\:*?"<>|]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    return name.strip('. ')[:200]

countries = {'泰國': THAILAND_COORDS, '韓國': KOREA_COORDS}

for country, ranges in countries.items():
    print(f"\n{'='*60}")
    print(f"補建 {country}")
    print(f"{'='*60}")
    
    kml_pois = extract_pois(ranges, country)
    wiki_names = get_wiki_names(country)
    
    missing = [p for p in kml_pois if p['name'].lower() not in wiki_names]
    print(f"發現缺失: {len(missing)} 個")
    
    created = 0
    for poi in missing:
        path = os.path.join(WIKI_BASE, country, "POI", "POI")
        os.makedirs(path, exist_ok=True)
        fname = f"{sanitize(poi['name'])}.md"
        fpath = os.path.join(path, fname)
        
        if not os.path.exists(fpath):
            content = f"---\ntitle: {poi['name']}\ncoordinates: [{poi['lng']}, {poi['lat']}]\n---\n# {poi['name']}"
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            created += 1
    
    print(f"建立: {created} 個")
