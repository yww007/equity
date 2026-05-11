# A股财务指标排名网站

一个展示中国A股上市公司核心财务指标的静态网站，通过 GitHub Pages 部署。

## 功能

- 📊 展示 A 股上市公司财务指标排名
- 🔍 按公司名称/代码搜索
- 📈 多维度排序（PE、PB、PEG、ROE、毛利率、净利率、净利润增长率、营业收入增长率等）
- 🏭 按行业筛选
- 🌙 深色模式支持
- 📱 响应式设计

## 指标说明

| 指标 | 说明 |
|------|------|
| 市盈率 (PE) | 股价 / 每股收益 |
| 市净率 (PB) | 股价 / 每股净资产 |
| PEG | 市盈率 / 净利润增长率 |
| ROE | 净资产收益率 = 净利润 / 净资产 |
| 毛利率 | (营业收入 - 营业成本) / 营业收入 |
| 净利率 | 净利润 / 营业收入 |
| 资产负债率 | 总负债 / 总资产 |
| 经营活动现金流净额 | 经营活动现金流量净额（亿元） |
| 净利润增长率 | 本期净利润 / 上期净利润 - 1（%） |
| 营业收入增长率 | 本期营收 / 上期营收 - 1（%） |

## 部署

### GitHub Pages 部署（推荐）

1. 创建 GitHub 仓库 `equity`
2. 推送代码到 `master` 分支
3. 在 Settings → Pages 中选择 `master` 分支根目录
4. 访问 `https://<你的用户名>.github.io/equity/`

### 本地预览

```bash
python3 -m http.server 8000
# 访问 http://localhost:8000
```

## 数据更新

### 手动更新

```bash
pip install akshare pandas
python fetch_stocks.py
```

### 自动更新（GitHub Actions）

推送后自动触发：`.github/workflows/update_data.yml`

## 依赖

- 前端：纯 HTML/CSS/JavaScript，无框架
- 数据抓取：Python + akshare
- 部署：GitHub Pages

## 免责声明

本网站数据仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。
