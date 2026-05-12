# 百度地圖中世界地圖坐标点

## 参考

> [CSDN - echarts世界地圖各个國家及中国城市的经纬度数组](https://blog.csdn.net/xiaozhi_free/article/details/79654529)
>
> [CSDN - echarts世界國家中英文对照](https://blog.csdn.net/u012557538/article/details/78490267)

## 說明

- 基于百度坐标系，具体坐标系的区别，参见 [坐标系說明书](http://lbsyun.baidu.com/index.php?title=coordinate)
- 共计`174`个國家或地區的資料，如有缺失，请自行添加
- 政治相关
    - 國家英文名称，按照`world-map`中`name`字段为准，部分國家为展示，部分缩写
        - 如`Republic` 缩写为`Rep.`
        - `United States of America`改为`United States`
    - 國家英文名称，全称见`world-map`中`formal_en`字段
    - 不涉及政治区域的划分和地區与國家的讨论，及各种纠纷
        - 已删除“中华人民共和國台湾省”資料，需要者自行添加
        - `world-map`中國家，缺少`Côte d'Ivoire`及`Palestine`对应的國家中心点及中英文对照，需要者自行添加
        - 修改部分國家中文名称，如`北朝鲜`改为`朝鲜`

## 目录结构

```tree
.
├── README.md
├── world-country-center.json           # 世界國家中心点，已按照字典序排列
├── world-country-translation.json      # 世界國家中英文对照，已按照字典序排列
├── world-country.json                  # 世界國家資訊（已合并其他3个json資料）
├── world-map.json                      # 世界國家原始資料
└── world.js                            # 可直接运行
```
