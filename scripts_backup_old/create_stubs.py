import os

stubs = {
    "wiki/concepts/gangneung-city.md": "---\ntype: concept\ntitle: 江陵市 (Gangneung City)\naliases: [강릉시]\n---\n",
    "wiki/concepts/jeongdongjin.md": "---\ntype: concept\ntitle: 正東津 (Jeongdongjin)\naliases: [정동진]\n---\n",
    "wiki/concepts/yeongrangho-lake.md": "---\ntype: concept\ntitle: 永郎湖 (Yeongrangho Lake)\naliases: [영랑호]\n---\n",
    "wiki/concepts/sokcho-beach.md": "---\ntype: concept\ntitle: 束草海灘 (Sokcho Beach)\naliases: [속초해수욕장]\n---\n",
    "wiki/concepts/namdaecheon.md": "---\ntype: concept\ntitle: 南大川 (Namdaecheon)\naliases: [남대천]\n---\n",
    "wiki/concepts/hajodae-observatory.md": "---\ntype: concept\ntitle: 河趙台觀景台 (Hajodae Observatory)\naliases: [하조대전망대]\n---\n",
    "wiki/concepts/seoraksan-cable-car.md": "---\ntype: concept\ntitle: 雪嶽山纜車 (Seoraksan Cable Car)\naliases: [설악산케이블카]\n---\n",
    "wiki/concepts/woljeongsa-temple.md": "---\ntype: concept\ntitle: 月精寺 (Woljeongsa Temple)\n---\n",
    "wiki/entities/cheongnyangni-station.md": "---\ntype: entity\ntitle: 清涼里站 (Cheongnyangni Station)\naliases: [청량리역]\n---\n",
    "wiki/entities/xing-xing-office.md": "---\ntype: entity\ntitle: 星星事務所 (Xing-Xing Office)\naliases: [星星事務所]\n---\n",
    "wiki/entities/with-u-hotel-guesthouse.md": "---\ntype: entity\ntitle: With U Hotel & Guesthouse\n---\n",
    "wiki/entities/janggun-charcoal-bbq-buffet.md": "---\ntype: entity\ntitle: 將軍炭烤肉 (Janggun BBQ)\n---\n",
    "wiki/entities/ocean-train.md": "---\ntype: entity\ntitle: 海洋列車 (Ocean Train)\n---\n",
    "wiki/entities/sokcho-express-bus-terminal.md": "---\ntype: entity\ntitle: 束草高速巴士客運站 (Sokcho Express Bus Terminal)\n---\n",
    "wiki/entities/sinheungsa-temple.md": "---\ntype: entity\ntitle: 新興寺 (Sinheungsa Temple)\ndate: 2026-04-16\ntags: [korea, seoraksan, temple]\nentity_type: place\naliases: [신흥사]\n---\n\n## Description\n新興寺是位於雪嶽山國立公園內的一座古剎，最初由義湘大師於西元 652 年創建（當時名為香城寺）。它是進入雪嶽山登山步道的必經之地。\n\n## Key Contributions\n- **統一大佛**：新興寺最著名的標誌是一尊巨大的青銅坐佛（統一大佛），象徵著對於朝鮮半島南北和平統一的祈願。\n\n## Related Concepts\n- [[seoraksan-national-park]]\n- [[sinheungsa-grand-bronze-buddha]]\n\n## Sources\n- [[src-seoraksan-cable-car-ulsanbawi]]\n- [[src-gangwon-4d3n-itinerary]]\n"
}

for path, content in stubs.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
