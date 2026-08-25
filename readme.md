# 🎭 UZI 深度报告站

[UZI-Skill](https://github.com/wbh604/UZI-Skill)（66 位投资大佬评审团 × 9 流派 × 22 维数据 × 22 机构方法）生成的个股深度报告，经 AI Agent 自动发布。

**在线阅读**: https://fumolan.github.io/uzi-reports/
**RSS 订阅**: https://fumolan.github.io/uzi-reports/rss.xml

## 结构

- `reports/uzi/` — 报告正文（`.md` 摘要 + 完整 HTML）
- `scripts/update_index.py` — 扫描目录重建 `reports.json`
- `scripts/build_rss.py` — 从 `reports.json` 生成 `rss.xml`

## 免责

数据来自公开免费源，含缺口标记；报告由规则引擎+AI生成，不构成投资建议。
