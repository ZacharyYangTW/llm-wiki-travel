#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML to Wiki INGEST 自動化腳本（改進版）
功能：將 KML 景點批量轉換為 wiki markdown 檔案
增強功能：slug、tags、created_at、md5
"""

import xml.etree.ElementTree as ET
import os
import re
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import json

# 設定 UTF-8 編碼
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 設定路徑
KML_FILE = r"h:\我的雲端硬碟\llm_wiki_travel\raw\travel\Zachary's World Trip.kml"
WIKI_DIR = r"h:\我的雲端硬碟\llm_wiki_travel\wiki"
LOG_FILE = os.path.join(WIKI_DIR, "log.md")
INDEX_FILE = os.path.join(WIKI_DIR, "index.md")
DB_FILE = os.path.join(WIKI_DIR, "index.json")  # 為 indexer 準備的數據庫

# 國家與城市對應表（完整版）
COUNTRY_MAP = {
    # 中國大陸
    "北京": "中國",
    "上海": "中國",
    "廣州": "中國",
    "深圳": "中國",
    "杭州": "中國",
    "南京": "中國",
    "蘇州": "中國",
    "西安": "中國",
    "重慶": "中國",
    "成都": "中國",
    "武漢": "中國",
    "長沙": "中國",
    "南昌": "中國",
    "貴陽": "中國",
    "昆明": "中國",
    "鄭州": "中國",
    "洛陽": "中國",
    "開封": "中國",
    "曲阜": "中國",
    "泰安": "中國",
    "濟南": "中國",
    "青島": "中國",
    "煙台": "中國",
    "天津": "中國",
    "瀋陽": "中國",
    "大連": "中國",
    "長春": "中國",
    "哈爾濱": "中國",
    "西寧": "中國",
    "西寧": "中國",
    "銀川": "中國",
    "太原": "中國",
    "石家莊": "中國",
    "南寧": "中國",
    "海口": "中國",
    "三亞": "中國",
    "福州": "中國",
    "廈門": "中國",
    "泉州": "中國",
    "溫州": "中國",
    "紹興": "中國",
    "寧波": "中國",
    "合肥": "中國",
    "南陽": "中國",
    "荊州": "中國",
    "宜昌": "中國",
    "常德": "中國",
    "張家界": "中國",
    "婺源": "中國",
    "贛州": "中國",
    "上饒": "中國",
    "龍川": "中國",
    "梅州": "中國",
    "清遠": "中國",
    "肇慶": "中國",
    "佛山": "中國",
    "東莞": "中國",
    "惠州": "中國",
    "梧州": "中國",
    "玉林": "中國",
    "貴港": "中國",
    "柳州": "中國",
    "桂林": "中國",
    "衡陽": "中國",
    "邯鄲": "中國",
    "忻州": "中國",
    "運城": "中國",
    "臨汾": "中國",
    "吉安": "中國",
    "撫州": "中國",
    "景德鎮": "中國",
    "九江": "中國",
    "黃石": "中國",
    "黃岡": "中國",
    "咸寧": "中國",
    "孝感": "中國",
    "隨州": "中國",
    "恩施": "中國",
    "十堰": "中國",
    "襄陽": "中國",
    "鄂州": "中國",
    "益陽": "中國",
    "婁底": "中國",
    "邵陽": "中國",
    "懷化": "中國",
    "永州": "中國",
    "吉林": "中國",
    "通化": "中國",
    "白山": "中國",
    "松原": "中國",
    "遼源": "中國",
    "四平": "中國",
    "白城": "中國",
    "牡丹江": "中國",
    "綏化": "中國",
    "黑河": "中國",
    "大興安嶺": "中國",
    "克拉瑪依": "中國",
    "烏魯木齊": "中國",
    "吐魯番": "中國",
    "哈密": "中國",
    "昌吉": "中國",
    "博樂": "中國",
    "阿勒泰": "中國",
    "喀什": "中國",
    "和田": "中國",
    "阿克蘇": "中國",
    "巴音郭楞": "中國",
    "拉薩": "中國",
    "日喀則": "中國",
    "林芝": "中國",
    "昌都": "中國",
    "山南": "中國",
    "那曲": "中國",
    "阿里": "中國",
    "青海": "中國",
    "海東": "中國",
    "海北": "中國",
    "黃南": "中國",
    "玉樹": "中國",
    "果洛": "中國",
    "海南藏族": "中國",
    "海西蒙古族": "中國",
    "甘孜": "中國",
    "阿壩": "中國",
    "涼山": "中國",
    "巴中": "中國",
    "達州": "中國",
    "雅安": "中國",
    "眉山": "中國",
    "樂山": "中國",
    "自貢": "中國",
    "瀘州": "中國",
    "宜賓": "中國",
    "南充": "中國",
    "廣安": "中國",
    "遂寧": "中國",
    "內江": "中國",
    "資陽": "中國",
    "阿壩": "中國",
    "甘孜": "中國",
    "涼山": "中國",
    "陇南": "中國",
    "平凉": "中國",
    "庆阳": "中國",
    "天水": "中國",
    "张掖": "中國",
    "武威": "中國",
    "白银": "中國",
    "定西": "中國",
    "酒泉": "中國",
    "嘉峪关": "中國",
    "忻州": "中國",
    "朔州": "中國",
    "晋中": "中國",
    "长治": "中國",
    "晋城": "中國",
    "阳泉": "中國",
    "大同": "中國",
    "陆周": "中國",
    "吕梁": "中國",
    "商丘": "中國",
    "周口": "中國",
    "驻马店": "中國",
    "信阳": "中國",
    "南阳": "中國",
    "平顶山": "中國",
    "许昌": "中國",
    "漯河": "中國",
    "三门峡": "中國",
    "焦作": "中國",
    "新乡": "中國",
    "安阳": "中國",
    "濮阳": "中國",
    "鹤壁": "中國",
    "峨眉山": "中國",
    "九寨溝": "中國",
    "黃龍": "中國",
    "澳門": "中國",
    "香港": "中國",

    # 台灣（中華民國）- 完整縣市
    "台北": "台灣",
    "台北市": "台灣",
    "新北": "台灣",
    "新北市": "台灣",
    "基隆": "台灣",
    "桃園": "台灣",
    "新竹": "台灣",
    "新竹市": "台灣",
    "新竹縣": "台灣",
    "苗栗": "台灣",
    "台中": "台灣",
    "彰化": "台灣",
    "南投": "台灣",
    "雲林": "台灣",
    "嘉義": "台灣",
    "嘉義市": "台灣",
    "嘉義縣": "台灣",
    "台南": "台灣",
    "高雄": "台灣",
    "屏東": "台灣",
    "屏東東港": "台灣",
    "花蓮": "台灣",
    "台東": "台灣",
    "澎湖": "台灣",
    "綠島": "台灣",
    "蘭嶼": "台灣",
    "長灘島": "台灣",  # 東沙群島
    "台北陽明山": "台灣",
    "宜蘭": "台灣",
    "羅東": "台灣",
    "烏來": "台灣",
    "北投": "台灣",
    "士林": "台灣",
    "西門町": "台灣",
    "淡水": "台灣",
    "新店": "台灣",
    "永和": "台灣",
    "中和": "台灣",
    "板橋": "台灣",
    "內湖": "台灣",
    "景美": "台灣",
    "天母": "台灣",
    "石牌": "台灣",
    "一中": "台灣",
    "勤美": "台灣",
    "南科": "台灣",
    "虎尾": "台灣",
    "斗六": "台灣",
    "池上": "台灣",
    "冬山": "台灣",
    "礁溪": "台灣",
    "宜蘭市": "台灣",
    "蘇澳": "台灣",
    "金門": "台灣",
    "小金門": "台灣",
    "金城": "台灣",
    "墾丁": "台灣",
    "小琉球": "台灣",
    "日月潭": "台灣",
    "阿里山": "台灣",
    "合掌村": "台灣",  # 可能是日本
    "善化": "台灣",
    "麻豆": "台灣",

    # 日本 - 完整城市清單
    "東京": "日本",
    "新宿": "日本",
    "新宿Airbnb": "日本",
    "渋谷": "日本",
    "涉谷": "日本",
    "原宿": "日本",
    "池袋": "日本",
    "銀座": "日本",
    "中環": "日本",
    "成田": "日本",
    "成田T2": "日本",
    "成田機場": "日本",
    "都營新宿線": "日本",
    "都營新宿": "日本",
    "日光": "日本",
    "三鷹": "日本",
    "日本三鷹市": "日本",
    "江之島": "日本",
    "鎌倉": "日本",
    "鎌倉高校前": "日本",
    "横浜": "日本",
    "新浦安": "日本",
    "京都": "日本",
    "大阪": "日本",
    "大阪站": "日本",
    "JR大阪站": "日本",
    "心齋橋": "日本",
    "大阪心齋橋": "日本",
    "新大阪": "日本",
    "新大阪駅": "日本",
    "JR新大阪駅": "日本",
    "神戶": "日本",
    "兵庫姬路": "日本",
    "名古屋": "日本",
    "中部國際機場": "日本",
    "福岡": "日本",
    "廣島": "日本",
    "岡山": "日本",
    "倉敷": "日本",
    "倉敷 Ario": "日本",
    "高松": "日本",
    "德島": "日本",
    "香川": "日本",
    "愛媛": "日本",
    "高知": "日本",
    "佐賀": "日本",
    "長崎": "日本",
    "熊本": "日本",
    "大分": "日本",
    "宮崎": "日本",
    "鹿兒島": "日本",
    "沖繩": "日本",
    "那霸": "日本",
    "牧志": "日本",
    "國際通": "日本",
    "北谷": "日本",
    "名護": "日本",
    "美麗海水族館": "日本",
    "那霸公車總站": "日本",
    "玉泉洞": "日本",
    "奈良": "日本",
    "伊勢": "日本",
    "伊勢內宮前": "日本",
    "伊勢寶來亭": "日本",
    "和歌山": "日本",
    "三重": "日本",
    "滋賀": "日本",
    "岐阜": "日本",
    "愛知": "日本",
    "靜岡": "日本",
    "山梨": "日本",
    "長野": "日本",
    "松本": "日本",
    "高山": "日本",
    "高山市": "日本",
    "犬山": "日本",
    "信濃大町": "日本",
    "室堂": "日本",
    "扇沢": "日本",
    "富山": "日本",
    "富山站": "日本",
    "黑部湖": "日本",
    "黑部水壩": "日本",
    "立山": "日本",
    "立山黑部郵局": "日本",
    "新潟": "日本",
    "石川": "日本",
    "福井": "日本",
    "栃木": "日本",
    "群馬": "日本",
    "埼玉": "日本",
    "千葉": "日本",
    "神奈川": "日本",
    "福島": "日本",
    "里磐梯湖畔渡假村": "日本",
    "宮城": "日本",
    "仙台": "日本",
    "岩手": "日本",
    "青森": "日本",
    "秋田": "日本",
    "山形": "日本",
    "北海道": "日本",
    "札幌": "日本",
    "函館": "日本",
    "旭川": "日本",
    "釧路": "日本",
    "帯広": "日本",
    "稚內": "日本",
    "洞爺湖": "日本",
    "富士山": "日本",
    "箱根": "日本",
    "早雲山": "日本",
    "大觀峯": "日本",
    "石牌": "日本",
    "宮古島": "日本",
    "石垣島": "日本",

    # 韓國
    "首爾": "韓國",
    "釜山": "韓國",
    "仁川": "韓國",
    "大邱": "韓國",
    "大田": "韓國",
    "光州": "韓國",
    "울산": "韓國",
    "世宗": "韓國",
    "京畿": "韓國",
    "江原": "韓國",
    "忠清北道": "韓國",
    "忠清南道": "韓國",
    "全北": "韓國",
    "全南": "韓國",
    "慶尚北道": "韓國",
    "慶尚南道": "韓國",
    "濟州": "韓國",

    # 菲律賓
    "馬尼拉": "菲律賓",
    "長灘島": "菲律賓",
    "宿務": "菲律賓",
    "達沃": "菲律賓",
    "克拉克": "菲律賓",
    "碧瑤": "菲律賓",
    "八打雁": "菲律賓",
    "馬尼拉灣": "菲律賓",
    "巴拿威": "菲律賓",

    # 東南亞其他
    "曼谷": "泰國",
    "清邁": "泰國",
    "普吉島": "泰國",
    "芭堤雅": "泰國",
    "新加坡": "新加坡",
    "檳城": "馬來西亞",
    "吉隆坡": "馬來西亞",
    "馬六甲": "馬來西亞",
    "仰光": "緬甸",
    "河內": "越南",
    "胡志明市": "越南",
    "順化": "越南",
    "會安": "越南",
    "峴港": "越南",
    "金邊": "柬埔寨",
    "暹粒": "柬埔寨",
    "聖殿灣": "柬埔寨",
    "朱拉隆功": "老撾",
    "琅勃拉邦": "老撾",

    # 南亞
    "新德里": "印度",
    "孟買": "印度",
    "加爾各答": "印度",
    "班加羅爾": "印度",
    "金奈": "印度",
    "德里": "印度",
    "齋浦爾": "印度",
    "阿格拉": "印度",
    "瓦拉納西": "印度",
    "達卡": "孟加拉國",
    "吉大港": "孟加拉國",
    "科倫坡": "斯里蘭卡",
    "康堤": "斯里蘭卡",
    "加德滿都": "尼泊爾",
    "博卡拉": "尼泊爾",
    "卡德斯": "巴基斯坦",
    "伊斯蘭堡": "巴基斯坦",
    "拉合爾": "巴基斯坦",

    # 中東
    "迪拜": "阿聯酋",
    "阿布扎比": "阿聯酋",
    "沙迦": "阿聯酋",
    "阿吉曼": "阿聯酋",
    "利雅得": "沙烏地阿拉伯",
    "吉達": "沙烏地阿拉伯",
    "麥加": "沙烏地阿拉伯",
    "伊斯坦布爾": "土耳其",
    "安卡拉": "土耳其",
    "伊茲密爾": "土耳其",
    "特洛伊": "土耳其",
    "卡帕多奇亞": "土耳其",
    "帕慕卡麗": "土耳其",
    "聖城": "以色列",
    "特拉維夫": "以色列",
    "死海": "以色列",
    "埃拉特": "以色列",
    "安曼": "約旦",
    "佩特拉": "約旦",
    "死海": "約旦",
    "開羅": "埃及",
    "吉薩": "埃及",
    "盧克索": "埃及",
    "阿斯旺": "埃及",
    "貝魯特": "黎巴嫩",

    # 歐洲
    "倫敦": "英國",
    "伯明罕": "英國",
    "曼徹斯特": "英國",
    "利物浦": "英國",
    "愛丁堡": "英國",
    "溫莎": "英國",
    "巴黎": "法國",
    "馬賽": "法國",
    "里昂": "法國",
    "尼斯": "法國",
    "普羅旺斯": "法國",
    "盧瓦爾河谷": "法國",
    "慕尼黑": "德國",
    "柏林": "德國",
    "科隆": "德國",
    "漢堡": "德國",
    "斯圖加特": "德國",
    "法蘭克福": "德國",
    "羅馬": "義大利",
    "米蘭": "義大利",
    "威尼斯": "義大利",
    "佛羅倫斯": "義大利",
    "那不勒斯": "義大利",
    "托斯卡納": "義大利",
    "五漁村": "義大利",
    "馬德里": "西班牙",
    "巴塞隆納": "西班牙",
    "塞維利亞": "西班牙",
    "格拉納達": "西班牙",
    "托萊多": "西班牙",
    "里斯本": "葡萄牙",
    "波爾圖": "葡萄牙",
    "阿姆斯特丹": "荷蘭",
    "鹿特丹": "荷蘭",
    "烏得勒支": "荷蘭",
    "布魯塞爾": "比利時",
    "安特衛普": "比利時",
    "布魯日": "比利時",
    "日內瓦": "瑞士",
    "蘇黎世": "瑞士",
    "伯爾尼": "瑞士",
    "盧塞恩": "瑞士",
    "因特拉肯": "瑞士",
    "維也納": "奧地利",
    "薩爾茨堡": "奧地利",
    "因斯布魯克": "奧地利",
    "布拉格": "捷克",
    "卡羅維瓦里": "捷克",
    "克魯姆洛夫": "捷克",
    "布達佩斯": "匈牙利",
    "克拉科夫": "波蘭",
    "華沙": "波蘭",
    "格但斯克": "波蘭",
    "布加勒斯特": "羅馬尼亞",
    "布拉索夫": "羅馬尼亞",
    "錫比烏": "羅馬尼亞",
    "索菲亞": "保加利亞",
    "雅典": "希臘",
    "聖托里尼": "希臘",
    "米克諾斯": "希臘",
    "克里特島": "希臘",
    "羅德島": "希臘",
    "德爾斐": "希臘",
    "莫斯科": "俄羅斯",
    "聖彼得堡": "俄羅斯",
    "新西伯利亞": "俄羅斯",
    "葉卡捷琳堡": "俄羅斯",
    "基輔": "烏克蘭",
    "利沃夫": "烏克蘭",
    "明斯克": "白俄羅斯",
    "里加": "拉脫維亞",
    "塔林": "愛沙尼亞",
    "維爾紐斯": "立陶宛",
    "斯德哥爾摩": "瑞典",
    "哥德堡": "瑞典",
    "馬爾默": "瑞典",
    "奧斯陸": "挪威",
    "卑爾根": "挪威",
    "特隆赫姆": "挪威",
    "哥本哈根": "丹麥",
    "奧胡斯": "丹麥",
    "雷克雅未克": "冰島",
    "赫爾辛基": "芬蘭",
    "圖爾庫": "芬蘭",

    # 北美
    "紐約": "美國",
    "洛杉磯": "美國",
    "芝加哥": "美國",
    "休斯頓": "美國",
    "鳳凰城": "美國",
    "費城": "美國",
    "聖安東尼奧": "美國",
    "聖地牙哥": "美國",
    "達拉斯": "美國",
    "聖何塞": "美國",
    "舊金山": "美國",
    "西雅圖": "美國",
    "波士頓": "美國",
    "邁阿密": "美國",
    "亞特蘭大": "美國",
    "丹佛": "美國",
    "底特律": "美國",
    "明尼阿波利斯": "美國",
    "聖路易": "美國",
    "新奧爾良": "美國",
    "拉斯維加斯": "美國",
    "黃石": "美國",
    "大峽谷": "美國",
    "優勝美地": "美國",
    "托斯坦": "美國",
    "夏威夷": "美國",
    "阿拉斯加": "美國",
    "多倫多": "加拿大",
    "蒙特利爾": "加拿大",
    "溫哥華": "加拿大",
    "卡爾加里": "加拿大",
    "魁北克": "加拿大",
    "埃德蒙頓": "加拿大",
    "渥太華": "加拿大",
    "尼亞加拉大瀑布": "加拿大",
    "班芙": "加拿大",
    "洛磯山脈": "加拿大",
    "墨西哥城": "墨西哥",
    "坎昆": "墨西哥",
    "瓜納華托": "墨西哥",
    "瓦哈卡": "墨西哥",
    "聖米格爾德阿連德": "墨西哥",
    "聖地牙哥": "墨西哥",
    "巴亞爾塔港": "墨西哥",
    "普拉亞德爾卡門": "墨西哥",

    # 中美洲與加勒比
    "聖胡安": "波多黎各",
    "聖聖多明各": "多米尼加",
    "聖地亞哥德古巴": "古巴",
    "哈瓦那": "古巴",
    "蒙特哥灣": "牙買加",
    "金斯敦": "牙買加",
    "拿騷": "巴哈馬",
    "聖約翰": "聖露西亞",
    "卡斯特里": "聖露西亞",

    # 南美洲
    "里約熱內盧": "巴西",
    "聖保羅": "巴西",
    "薩爾瓦多": "巴西",
    "馬瑙斯": "巴西",
    "庫裡提巴": "巴西",
    "伊瓜蘇": "巴西",
    "布宜諾斯艾利斯": "阿根廷",
    "門多薩": "阿根廷",
    "科爾多瓦": "阿根廷",
    "巴里洛切": "阿根廷",
    "聖卡洛斯德巴里洛切": "阿根廷",
    "聖地亞哥": "智利",
    "聖地亞哥": "智利",
    "瓦爾帕萊索": "智利",
    "聖佩德羅德阿塔卡瑪": "智利",
    "復活節島": "智利",
    "利馬": "秘魯",
    "馬丘比丘": "秘魯",
    "庫斯科": "秘魯",
    "普諾": "秘魯",
    "拉巴斯": "玻利維亞",
    "蘇克雷": "玻利維亞",
    "聖克魯斯": "玻利維亞",
    "烏尤尼": "玻利維亞",
    "卡拉卡斯": "委內瑞拉",
    "馬拉開波": "委內瑞拉",
    "波哥大": "哥倫比亞",
    "卡塔赫納": "哥倫比亞",
    "聖安德烈斯": "哥倫比亞",
    "基多": "厄瓜多爾",
    "瓜亞基爾": "厄瓜多爾",
    "馬拉": "厄瓜多爾",
    "萬科沃": "厄瓜多爾",
    "利馬": "秘魯",
    "巴拿馬城": "巴拿馬",
    "聖布拉斯群島": "巴拿馬",
    "卡斯蒂略聖費利佩": "巴拿馬",
    "喬科": "巴拿馬",

    # 大洋洲
    "悉尼": "澳洲",
    "墨爾本": "澳洲",
    "布里斯班": "澳洲",
    "珀斯": "澳洲",
    "阿德萊德": "澳洲",
    "霍巴特": "澳洲",
    "艾麗斯泉": "澳洲",
    "烏魯魯": "澳洲",
    "大堡礁": "澳洲",
    "塔斯馬尼亞": "澳洲",
    "新西蘭": "紐西蘭",
    "奧克蘭": "紐西蘭",
    "惠靈頓": "紐西蘭",
    "基督城": "紐西蘭",
    "皇后鎮": "紐西蘭",
    "羅托魯瓦": "紐西蘭",
    "毛伊島": "紐西蘭",
    "斐濟": "斐濟",
    "楠迪": "斐濟",
    "蘇瓦": "斐濟",
    "湯加": "湯加",
    "努庫阿洛法": "湯加",
    "薩摩亞": "薩摩亞",
    "帕果帕果": "美屬薩摩亞",
    "阿皮亞": "薩摩亞",
    "帛琉": "帛琉",
    "科羅爾": "帛琉",
    "關島": "美國",
    "馬裡亞納群島": "美國",
    "塹班": "美國",

    # 英文城市代碼與別名
    "TPE": "台灣",  # Taipei Taoyuan
    "LAX": "美國",  # Los Angeles
    "LA": "美國",  # Los Angeles
    "SFO": "美國",  # San Francisco
    "IAH": "美國",  # Houston
    "Houston": "美國",
    "Austin": "美國",
    "San Antonio": "美國",
    "Las Vegas": "美國",
    "Santa Monica": "美國",
    "Saigon": "越南",  # Ho Chi Minh City
    "Saigon Centre": "越南",
    "Lima": "秘魯",
    "Cusco": "秘魯",
    "Easter Island": "智利",  # Rapa Nui
    "Paracas": "秘魯",
    "Nasca": "秘魯",
    "BCN": "西班牙",  # Barcelona
    "Prague": "捷克",  # Prague
    "prague": "捷克",
    "budapest": "匈牙利",
    "Liège": "比利時",
    "Gent": "比利時",
    "Gent Sint": "比利時",
    "Antwerpen": "比利時",
    "Steenwijk": "荷蘭",
    "NRT": "日本",  # Narita
    "KIX": "日本",  # Kansai
    "BKK": "泰國",  # Bangkok
    "AKL": "紐西蘭",  # Auckland
    "OKA": "日本",  # Okinawa
    "MEL": "澳洲",  # Melbourne
    "HBA": "澳洲",  # Hobart
    "MFK": "美國",  # Maryland/DC
    "NKG": "中國",  # Nanjing
    "SZX": "中國",  # Shenzhen
    "XMN": "中國",  # Xiamen
    "FOC": "中國",  # Fuzhou
    "SCL": "智利",  # Santiago
    "FAI": "美國",  # Fairbanks
    "Fairbanks": "美國",
    "AUS": "美國",  # Austin
    "CTS": "中國",  # Zhengzhou
    "KMG": "中國",  # Kunming
    "TSA": "台灣",  # Taipei Songshan
    "SGN": "越南",  # Saigon
    "DAD": "越南",  # Da Nang
    "MYJ": "馬來西亞",  # Kuala Lumpur
    "BKK": "泰國",  # Bangkok
    "PRG": "捷克",  # Prague
    "VIE": "奧地利",  # Vienna
    "Yellowknife": "加拿大",
    "黃刀鎮": "加拿大",
}

# 分類對應的標籤
CATEGORY_TAGS = {
    "機場": ["交通", "飛行"],
    "飯店": ["住宿", "旅館"],
    "餐廳": ["美食", "飲食"],
    "景點": ["觀光", "遊覽"],
    "交通樞紐": ["交通", "運輸"],
}

class KMLIngestor:
    def __init__(self):
        self.placemarks = []
        self.created_files = []
        self.failed_items = []
        self.db_entries = []
        self.unknown_cities = {}  # 記錄未識別的城市

    def parse_kml(self):
        """解析 KML 檔案"""
        print(f"讀取 KML 檔案: {KML_FILE}")
        try:
            tree = ET.parse(KML_FILE)
            root = tree.getroot()

            # KML 命名空間
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            # 提取所有 Placemark
            for placemark in root.findall('.//kml:Placemark', ns):
                name_elem = placemark.find('kml:name', ns)
                desc_elem = placemark.find('kml:description', ns)
                point_elem = placemark.find('kml:Point', ns)

                name = name_elem.text.strip() if name_elem is not None and name_elem.text else ''
                description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ''

                # 移除 CDATA 包裝
                description = description.replace('<![CDATA[', '').replace(']]>', '')
                # 移除 HTML 標籤
                description = re.sub(r'<br\s*/?>', '\n', description)
                description = re.sub(r'<[^>]+>', '', description)

                # 提取座標
                coords_text = ''
                if point_elem is not None:
                    coords_elem = point_elem.find('kml:coordinates', ns)
                    if coords_elem is not None and coords_elem.text:
                        coords_text = coords_elem.text.strip()

                coords = coords_text.split(',') if coords_text else [0, 0, 0]

                if name:
                    self.placemarks.append({
                        'name': name,
                        'description': description,
                        'longitude': float(coords[0]) if len(coords) > 0 else 0,
                        'latitude': float(coords[1]) if len(coords) > 1 else 0,
                    })

            print(f"成功解析 {len(self.placemarks)} 個景點")
            return True

        except Exception as e:
            print(f"解析失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

    def extract_location(self, description):
        """從 description 提取國家和城市"""
        if '-' in description:
            city = description.split('-')[0].strip()
            country = COUNTRY_MAP.get(city)

            if country is None:
                # 記錄未識別的城市
                self.unknown_cities[city] = self.unknown_cities.get(city, 0) + 1
                country = "其他"

            return country, city
        return "未知", "未分類"

    def slugify(self, text):
        """轉換為 slug (英文小寫+連字符)"""
        # 先轉換為拼音（簡化版，保留英文和數字）
        slug = re.sub(r'[^\w\s-]', '', text)
        slug = re.sub(r'[\s]+', '-', slug).lower()
        # 移除連續連字符
        slug = re.sub(r'-+', '-', slug)
        return slug[:64]  # 限制長度

    def generate_md5(self, name, description):
        """生成 MD5 去重 ID"""
        content = f"{name}|{description}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def infer_category_and_tags(self, name):
        """推斷分類和標籤"""
        if '機場' in name or '空港' in name or 'Airport' in name:
            category = "機場"
        elif '飯店' in name or '酒店' in name or '旅館' in name or 'Hotel' in name or 'Inn' in name:
            category = "飯店"
        elif '站' in name or '站' in name or 'Station' in name:
            category = "交通樞紐"
        elif '餐' in name or '餐廳' in name or '美食' in name or 'Restaurant' in name:
            category = "餐廳"
        else:
            category = "景點"

        tags = list(CATEGORY_TAGS.get(category, ["景點"]))
        return category, tags

    def create_frontmatter(self, placemark, country, city, category, slug, md5, tags):
        """生成 frontmatter"""
        created_at = datetime.now().isoformat() + 'Z'

        # 根據分類，決定是否需要特殊欄位
        extra_fields = ""
        if category == "餐廳":
            extra_fields = """
# 餐廳特定欄位（待擴充）
cuisine:
  dishes: []  # [{name_zh, name_local, name_en}, ...]
price_range: null  # $, $$, $$$, $$$$
```"""
        elif category == "飯店":
            extra_fields = """
# 飯店特定欄位（待擴充）
price_per_night: null  # 每晚價格
amenities: []  # 設施列表
check_in: null  # 入住時間
check_out: null  # 退房時間
```"""
        elif category == "景點":
            extra_fields = """
# 景點特定欄位（待擴充）
entry_fee: null  # 門票價格
hours:
  monday: null
  tuesday: null
  wednesday: null
  thursday: null
  friday: null
  saturday: null
  sunday: null
```"""

        frontmatter = f"""---
title: {placemark['name']}
slug: {slug}
location: {city}
country: {country}
city: {city}
category: {category}
tags: {json.dumps(tags, ensure_ascii=False)}
coordinates: [{placemark['longitude']}, {placemark['latitude']}]
md5: {md5}

# Google Maps 資訊（待擴充）
google_maps_url: null
rating: null  # 星級評分 (1-5)
review_count: null  # 評價數量
opening_hours: null  # 營業時間，待補充

# 共通擴充欄位（待補充）
entry_fee: null  # 費用
reviews_summary: null  # 10則評價重點整理
images: []  # 圖片連結

created_at: {created_at}
processed: false
graph-excluded: false
source_url: raw/travel/Zachary's World Trip.kml
source_type: kml-placemark
---
"""
        return frontmatter

    def create_markdown(self, placemark, country, city, category):
        """生成完整的 markdown 內容"""
        slug = self.slugify(placemark['name'])
        md5 = self.generate_md5(placemark['name'], placemark['description'])
        category, tags = self.infer_category_and_tags(placemark['name'])

        frontmatter = self.create_frontmatter(placemark, country, city, category, slug, md5, tags)

        # 根據分類建立不同的內容結構
        if category == "餐廳":
            body = f"""# {placemark['name']}

## 基本資訊

**位置：** {city}
**國家：** {country}
**座標：** {placemark['longitude']:.6f}°E, {placemark['latitude']:.6f}°N

## 描述

{placemark['description'] if placemark['description'] else '無描述'}

## Google Maps 資訊（待擴充）

- **評分：** 待補充
- **評價數：** 待補充
- **Google Maps 連結：** 待補充

## 營業時間（待擴充）

| 星期 | 時間 |
|------|------|
| 星期一 | 待補充 |
| 星期二 | 待補充 |
| 星期三 | 待補充 |
| 星期四 | 待補充 |
| 星期五 | 待補充 |
| 星期六 | 待補充 |
| 星期日 | 待補充 |

## 推薦菜色（待擴充）

| 中文 | 當地語言 | 英文 | 備註 |
|------|---------|------|------|
| 待補充 | 待補充 | 待補充 | |
| 待補充 | 待補充 | 待補充 | |
| 待補充 | 待補充 | 待補充 | |
| 待補充 | 待補充 | 待補充 | |
| 待補充 | 待補充 | 待補充 | |

## 評價整理（待擴充）

### 綜合評價
待補充（10則評價重點整理）

## 相關連結

- Google Maps: 待補充
- 官方網站: 待補充
"""

        elif category == "飯店":
            body = f"""# {placemark['name']}

## 基本資訊

**位置：** {city}
**國家：** {country}
**座標：** {placemark['longitude']:.6f}°E, {placemark['latitude']:.6f}°N

## 描述

{placemark['description'] if placemark['description'] else '無描述'}

## Google Maps 資訊（待擴充）

- **評分：** 待補充
- **評價數：** 待補充
- **Google Maps 連結：** 待補充

## 房價資訊（待擴充）

- **每晚價格：** 待補充
- **價格範圍：** 待補充

## 營業時間（待擴充）

| 項目 | 時間 |
|------|------|
| 入住時間 | 待補充 |
| 退房時間 | 待補充 |

## 設施介紹（待擴充）

待補充

## 評價整理（待擴充）

### 綜合評價
待補充（10則評價重點整理）

## 相關連結

- Google Maps: 待補充
- 官方網站: 待補充
"""

        else:  # 景點、機場、交通樞紐等
            body = f"""# {placemark['name']}

## 基本資訊

**位置：** {city}
**國家：** {country}
**座標：** {placemark['longitude']:.6f}°E, {placemark['latitude']:.6f}°N

## 描述

{placemark['description'] if placemark['description'] else '無描述'}

## Google Maps 資訊（待擴充）

- **評分：** 待補充
- **評價數：** 待補充
- **Google Maps 連結：** 待補充

## 營業時間（待擴充）

| 星期 | 時間 |
|------|------|
| 星期一 | 待補充 |
| 星期二 | 待補充 |
| 星期三 | 待補充 |
| 星期四 | 待補充 |
| 星期五 | 待補充 |
| 星期六 | 待補充 |
| 星期日 | 待補充 |

## 票價資訊（待擴充）

待補充

## 評價整理（待擴充）

### 綜合評價
待補充（10則評價重點整理）

## 相關連結

- Google Maps: 待補充
- 官方網站: 待補充
"""

        return frontmatter + body, slug, md5, tags

    def is_noise(self, name, city, longitude, latitude):
        """判斷是否為噪音數據（需要過濾）"""
        # 1. 過濾 [0, 0] 座標
        if longitude == 0.0 and latitude == 0.0:
            return True

        # 2. 過濾明顯的非城市項目（餐廳、便利店、公車線路等）
        noise_keywords = [
            "餐廳", "飯店", "餐", "吃", "咖啡", "麵", "肉", "火鍋", "湯",
            "便利店", "超市", "藥妝", "藥局", "購物", "商店", "百貨",
            "公車", "線", "班次", "停靠", "站台", "接駁", "時刻", "車",
            "機場線", "巴士", "shuttle", "transport", "stop", "station",
            "機場大巴", "酒店接駁", "付費公車", "Flyaway",
            "租車", "租賃", "Rent", "Rental",
            "ATM", "銀行", "郵局", "Post", "票券", "退稅", "換錢",
            "廁所", "洗手間", "bathroom",
            "駐車場", "停車", "Parking",
            "Line", "line", "Times", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday", "Departure",
            "Stop", "停", "時刻表", "運時",
            "新宿線", "都營", "JR", "駅", "Ekimae", "Ekimae",
            "Airbnb", "民宿", "旅館", "Hostel",
            "貸車", "Rent", "Car",
            "Ticket", "HOTEL", "MOTEL", "INN", "Resort",
            "Café", "café", "Coffee", "Bar", "Pub", "Restaurant",
            "酒吧", "夜店", "酒廊",
            "http", "https", "www", "триpadvisor", "ipeen",
            "Facebook", "instagram", "youtube",
            "日期", "時間", "地址", "座標", "map", "GPS",
            "註解", "備註", "說明", "描述",
            "接駁巴士", "免費", "收費", "價格", "元",
            "北大阪", "南浦洞", "光化門",
            "藝術", "文化", "展覽", "美術",
        ]

        # 檢查名稱中是否包含噪音關鍵字
        name_lower = name.lower()
        for keyword in noise_keywords:
            if keyword.lower() in name_lower:
                # 例外：某些包含關鍵字但仍是城市的項目
                if any(exc in name for exc in ["澳門", "東京", "大阪", "京都"]):
                    return False
                return True

        return False

    def ingest_all(self):
        """批量攝入所有景點"""
        print(f"\n開始攝入 {len(self.placemarks)} 個景點...")
        skipped_noise = 0

        for i, placemark in enumerate(self.placemarks, 1):
            # 檢查是否為噪音（過濾 [0,0] 座標和非城市項目）
            if self.is_noise(placemark['name'], placemark.get('city', ''),
                           placemark['longitude'], placemark['latitude']):
                skipped_noise += 1
                continue

            try:
                # 提取位置資訊
                country, city = self.extract_location(placemark['description'])

                # 推斷分類和標籤
                category, tags = self.infer_category_and_tags(placemark['name'])

                # 建立目錄
                dir_path = os.path.join(WIKI_DIR, country, city)
                os.makedirs(dir_path, exist_ok=True)

                # 生成檔案名
                file_name = f"{placemark['name']}.md"
                file_path = os.path.join(dir_path, file_name)

                # 生成內容
                content, slug, md5, tags = self.create_markdown(placemark, country, city, category)

                # 寫入檔案
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.created_files.append({
                    'path': file_path,
                    'name': placemark['name'],
                    'country': country,
                    'city': city,
                    'category': category,
                    'slug': slug,
                    'md5': md5,
                    'tags': tags,
                })

                # 為數據庫建立條目（供 indexer.py 和 searcher.py 使用）
                self.db_entries.append({
                    'title': placemark['name'],
                    'slug': slug,
                    'country': country,
                    'city': city,
                    'category': category,
                    'tags': tags,
                    'coordinates': {
                        'lng': placemark['longitude'],
                        'lat': placemark['latitude'],
                    },
                    'md5': md5,
                    'file_path': file_path.replace('\\', '/'),
                    'created_at': datetime.now().isoformat() + 'Z',
                    # 待擴充欄位
                    'google_maps': {
                        'url': None,
                        'rating': None,
                        'review_count': None,
                    },
                    'opening_hours': None,  # 營業時間
                    'entry_fee': None,  # 費用
                    'reviews_summary': None,  # 評價重點
                    'images': [],  # 圖片
                    'cuisine': None if category != '餐廳' else [],  # 餐廳菜色
                    'amenities': None if category != '飯店' else [],  # 飯店設施
                })

                # 進度顯示
                if i % 500 == 0:
                    print(f"  進度: {i}/{len(self.placemarks)} ({i/len(self.placemarks)*100:.1f}%)")

            except Exception as e:
                self.failed_items.append({
                    'name': placemark['name'],
                    'error': str(e)
                })
                if i % 500 == 0:
                    print(f"  失敗: {placemark['name']} - {e}")

        print(f"\n完成！已建立 {len(self.created_files)} 個景點檔案")
        print(f"已過濾噪音: {skipped_noise} 個項目")
        if self.failed_items:
            print(f"警告: 失敗 {len(self.failed_items)} 個景點")

        return True

    def update_log(self):
        """更新 wiki/log.md"""
        print("更新 log.md...")

        # 按國家和城市分組統計
        stats = {}
        for item in self.created_files:
            key = f"{item['country']}/{item['city']}"
            if key not in stats:
                stats[key] = {'count': 0, 'categories': {}}
            stats[key]['count'] += 1
            cat = item['category']
            stats[key]['categories'][cat] = stats[key]['categories'].get(cat, 0) + 1

        # 生成 log 內容
        log_content = f"""# Wiki 攝入日誌 (Ingest Log)

**最後更新：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 統計摘要

- **總景點數：** {len(self.created_files)}
- **失敗數：** {len(self.failed_items)}
- **地區數：** {len(stats)}

## 按地區統計

"""

        for location in sorted(stats.keys()):
            info = stats[location]
            log_content += f"\n### {location}\n"
            log_content += f"- 景點數：{info['count']}\n"
            for cat, count in sorted(info['categories'].items()):
                log_content += f"  - {cat}：{count}\n"

        # 寫入 log 檔案
        log_dir = os.path.dirname(LOG_FILE)
        os.makedirs(log_dir, exist_ok=True)

        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(log_content)

        print("log.md 已更新")

    def save_index_json(self):
        """保存 JSON 索引供 indexer.py 使用"""
        print("生成 index.json...")

        index_data = {
            'generated_at': datetime.now().isoformat() + 'Z',
            'total_entries': len(self.db_entries),
            'entries': self.db_entries,
        }

        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        print(f"index.json 已生成 ({len(self.db_entries)} 條目)")

    def run(self):
        """執行完整流程"""
        print("=" * 60)
        print("KML to Wiki INGEST 自動化腳本（改進版）")
        print("=" * 60)

        if self.parse_kml():
            self.ingest_all()
            self.update_log()
            self.save_index_json()

            print("\n" + "=" * 60)
            print("攝入完成！")
            print("=" * 60)
            print(f"檔案位置: {WIKI_DIR}")
            print(f"索引數據庫: {DB_FILE}")

            # 報告未識別的城市
            if self.unknown_cities:
                print("\n" + "=" * 60)
                print("警告：以下城市未被識別（已分類為「其他」）")
                print("=" * 60)
                for city, count in sorted(self.unknown_cities.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {city:20} {count:5} 個景點")
                print("\n提示: 請告訴我這些城市的正確國家，我會更新 COUNTRY_MAP")
            else:
                print("\n所有城市都被正確識別！")
        else:
            print("程式結束")

if __name__ == "__main__":
    ingestor = KMLIngestor()
    ingestor.run()
