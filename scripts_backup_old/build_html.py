import os

with open("raw/personal/itinerary.html", "r", encoding="utf-8") as f:
    content = f.read()

mermaid_script = """
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({startOnLoad:true, theme: 'base', themeVariables: { primaryColor: '#f8fafc', primaryTextColor: '#1e293b', primaryBorderColor: '#cbd5e1', lineColor: '#94a3b8' }});</script>
</head>
"""
content = content.replace("</head>", mermaid_script)

mermaid_diagram = """
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center overflow-x-auto my-8">
                <h3 class="text-xl font-bold mb-4 w-full text-left border-b pb-2"><i class="fa-solid fa-code-merge text-primary"></i> 知識庫推薦美食路線 (Mermaid Flowchart)</h3>
                <div class="mermaid">
flowchart LR
    subgraph Day1 [5/29 Day 1: 束草]
        L1(午: 束草水產市場<br>生魚片/海鮮)
        D1(晚: 將軍炭烤肉<br>With U側 ₩15k)
        L1 --> D1
    end
    subgraph Day2 [5/30 Day 2: 雪嶽山]
        L2(午: 雪濃湯<br>新興寺周邊)
        A2(午茶: 阿爸村<br>魷魚米腸/渡船)
        D2(晚: 束草炸雞<br>外帶回Hostel)
        L2 --> A2 --> D2
    end
    subgraph Day3 [5/31 Day 3: 江陵]
        L3(午: 江陵海鮮拌飯<br>東岸經典)
        D3(下茶: 安木咖啡街<br>觀海喝咖啡)
        L3 --> D3
    end
    subgraph Day4 [6/1 Day 4: 注文津]
        L4(午: 注文津海港<br>巨型螃蟹料理)
    end

    Day1 --> Day2 --> Day3 --> Day4
    
    classDef lunch fill:#d4af37,stroke:#b48c22,color:#ffffff,font-weight:bold,rx:8px,ry:8px;
    classDef dinner fill:#1e293b,stroke:#0f172a,color:#ffffff,rx:8px,ry:8px;
    classDef snack text-align:center,rx:8px,ry:8px;
    class L1,L2,L3,L4 lunch;
    class D1,D2,D3 dinner;
    class A2 snack;
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6" id="food-grid">
"""

content = content.replace('<div class="grid grid-cols-1 md:grid-cols-2 gap-6" id="food-grid">', mermaid_diagram)

os.makedirs("wiki/outputs", exist_ok=True)
with open("wiki/outputs/enhanced-itinerary.html", "w", encoding="utf-8") as f:
    f.write(content)
