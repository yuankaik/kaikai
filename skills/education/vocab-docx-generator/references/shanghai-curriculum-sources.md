# 已确认可用的课标词汇来源

## 知乎文章（上海牛津英语）

### 沪教版小学各年级英语单词列表（100 赞）
- URL: https://zhuanlan.zhihu.com/p/589199309
- 作者整理了 3-6 年级上下学期的完整单词表
- 格式：单词 \t 中文（按 UNIT 分组）
- 提取方式：需要 CDP websocket（知乎文章，非回答）

### 牛津上海版小学英语词汇表（39 赞）
- URL: https://zhuanlan.zhihu.com/p/682892484
- 2024 版手动整理

### 小学英语（牛津上海版）单词汇总系列
- 汇总1（低年级）：https://zhuanlan.zhihu.com/p/433465279
- 汇总2（三四年级）：https://zhuanlan.zhihu.com/p/433466342
- 汇总3（五六年级）：https://zhuanlan.zhihu.com/p/433471018

## 知乎文章（部编版语文）

### 小学语文生字带拼音表 1-6 年级（注意 OCR 拼音可能有误）
- URL: https://zhuanlan.zhihu.com/p/672828001

## 重要发现

1. 上海语文已改用**部编版**（全国统一），非沪教版
2. 上海英语仍用**沪教版牛津**（上海教育出版社 + 牛津大学出版社）
3. 知乎文章 type: article 必须走 CDP 提取，zhihu_answer 工具无效
4. 知乎 API 对 curl 返回 40362，需走 Chrome CDP
