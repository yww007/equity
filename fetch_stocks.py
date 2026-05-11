#!/usr/bin/env python3
"""
A股上市公司财务指标数据抓取脚本
===============================
使用 akshare 库抓取 A 股核心财务数据，生成 stocks.json
供 index.html 展示。

安装依赖:
    pip install akshare pandas

用法:
    python fetch_stocks.py              # 抓取并更新 data/stocks.json
    python fetch_stocks.py --sample     # 使用本地缓存/示例模式
"""

import json
import os
import sys
import time
from datetime import datetime

# =============================================
# 配置
# =============================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "stocks.json")

# 抓取的股票列表（沪深300核心成分股，可按需修改）
# 格式: (股票代码, 名称)
STOCKS = [
    ("600519", "贵州茅台"),
    ("300750", "宁德时代"),
    ("000333", "美的集团"),
    ("601318", "中国平安"),
    ("300760", "迈瑞医疗"),
    ("600900", "长江电力"),
    ("002594", "比亚迪"),
    ("600276", "恒瑞医药"),
    ("600036", "招商银行"),
    ("002415", "海康威视"),
    ("601888", "中国中免"),
    ("601899", "紫金矿业"),
    ("000651", "格力电器"),
    ("601012", "隆基绿能"),
    ("000858", "五粮液"),
    ("600030", "中信证券"),
    ("601166", "兴业银行"),
    ("600309", "万华化学"),
    ("000725", "京东方A"),
    ("601088", "中国神华"),
    ("300059", "东方财富"),
    ("603288", "海天味业"),
    ("601857", "中国石油"),
    ("002475", "立讯精密"),
    ("600887", "伊利股份"),
    ("603259", "药明康德"),
    ("601668", "中国建筑"),
    ("603501", "韦尔股份"),
    ("688981", "中芯国际"),
    ("600941", "中国联通"),
]

# 交易所后缀
EXCHANGE_MAP = {
    "6": "sh",
    "0": "sz",
    "3": "sz",
    "4": "bj",
    "8": "bj",
}

def get_exchange(code):
    prefix = code[0]
    return EXCHANGE_MAP.get(prefix, "sh")


def fetch_data_real():
    """使用 akshare 抓取真实数据"""
    try:
        import akshare as ak
        import pandas as pd
    except ImportError:
        print("❌ 缺少依赖: pip install akshare pandas")
        sys.exit(1)

    results = []
    errors = []

    print(f"📡 开始抓取 {len(STOCKS)} 只股票的数据...")
    print("-" * 50)

    for idx, (code, name) in enumerate(STOCKS, 1):
        try:
            exchange = get_exchange(code)
            full_code = f"{code}.{exchange.upper()}"

            print(f"  [{idx}/{len(STOCKS)}] {name} ({full_code}) ... ", end="", flush=True)

            # 获取实时行情
            try:
                realtime = ak.stock_zh_a_spot_em()
                realtime_filtered = realtime[realtime["代码"] == code]
                if realtime_filtered.empty:
                    print("⚠ 无行情数据")
                    continue
                row = realtime_filtered.iloc[0]
                price = float(row.get("最新价", 0))
            except Exception:
                price = 0

            # 获取财务指标
            try:
                financial = ak.stock_financial_abstract_ths(symbol=full_code)
                fin_data = financial.iloc[0] if not financial.empty else {}
                pe = float(fin_data.get("市盈率", 0) if pd.notna(fin_data.get("市盈率", 0)) else 0)
                pb = float(fin_data.get("市净率", 0) if pd.notna(fin_data.get("市净率", 0)) else 0)
            except Exception:
                pe, pb = 0, 0

            # 获取详细财务数据（利润表）
            try:
                # 净资产收益率、毛利率、净利率等
                profit = ak.stock_financial_report_sina(stock=full_code, symbol="利润表")
                if not profit.empty:
                    # 取最新一期数据
                    latest = profit.iloc[0]
                    gross_margin = float(latest.get("营业收入", 0))
                    net_margin_val = float(latest.get("净利润", 0))
                    revenue = float(latest.get("营业收入", 0))
                    gross_margin_pct = round(gross_margin / revenue * 100, 1) if revenue else 0
                    net_margin_pct = round(net_margin_val / revenue * 100, 1) if revenue else 0
                else:
                    gross_margin_pct, net_margin_pct = 0, 0
            except Exception:
                gross_margin_pct, net_margin_pct = 0, 0

            # ROE
            try:
                balance = ak.stock_financial_report_sina(stock=full_code, symbol="资产负债表")
                if not balance.empty:
                    latest_bal = balance.iloc[0]
                    equity = float(latest_bal.get("股东权益合计", 0))
                    roe = round(net_margin_val / equity * 100, 1) if equity else 0
                    debt = float(latest_bal.get("负债合计", 0))
                    assets = float(latest_bal.get("资产总计", 0))
                    debt_ratio = round(debt / assets * 100, 1) if assets else 0
                else:
                    roe, debt_ratio = 0, 0
            except Exception:
                roe, debt_ratio = 0, 0

            # 经营现金流
            try:
                cf = ak.stock_financial_report_sina(stock=full_code, symbol="现金流量表")
                if not cf.empty:
                    latest_cf = cf.iloc[0]
                    cashflow = round(float(latest_cf.get("经营活动产生的现金流量净额", 0)) / 1e8, 1)
                else:
                    cashflow = 0
            except Exception:
                cashflow = 0

            # PEG 估算
            peg = round(pe / roe * 100, 2) if roe > 0 and pe > 0 else 0

            # 行业分类（简单映射，后续可优化）
            industry = "其他"

            results.append({
                "rank": idx,
                "name": name,
                "code": full_code,
                "exchange": exchange,
                "pe": round(pe, 1),
                "pb": round(pb, 1),
                "peg": round(peg, 2),
                "roe": round(roe, 1),
                "gross_margin": round(gross_margin_pct, 1),
                "net_margin": round(net_margin_pct, 1),
                "debt_ratio": round(debt_ratio, 1),
                "cashflow": cashflow,
                "industry": industry,
            })

            print(f"✅ PE={pe:.1f} ROE={roe:.1f}%")

            # 避免请求过快被封
            time.sleep(0.5)

        except Exception as e:
            errors.append(f"{code} {name}: {e}")
            print(f"❌ 失败: {e}")

    # 重新排 rank
    for i, r in enumerate(results):
        r["rank"] = i + 1

    print("-" * 50)
    print(f"✅ 成功: {len(results)} 只")
    if errors:
        print(f"❌ 失败: {len(errors)} 只")
        for e in errors:
            print(f"   - {e}")

    return results


def fetch_data_sample():
    """返回硬编码的示例数据（stocks.json 里的内容）"""
    sample_file = OUTPUT_FILE
    if os.path.exists(sample_file):
        with open(sample_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("data", data) if isinstance(data, dict) else data

    # fallback: 使用内置示例数据（从 index.html 中提取）
    print("⚠ 未找到现有 stocks.json，使用内置示例数据")
    return []  # 简化处理


def save_data(data):
    """保存数据到 JSON 文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 尝试读取行业信息，如果已有则保留
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
            for item in (old.get("data", old) if isinstance(old, dict) else old):
                if isinstance(item, dict) and "code" in item:
                    existing[item["code"]] = item.get("industry", "")
        except Exception:
            pass

    # 补全行业信息
    for item in data:
        if item.get("code") in existing and (not item.get("industry") or item["industry"] == "其他"):
            item["industry"] = existing[item["code"]]

    output = {
        "meta": {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data_date": datetime.now().strftime("%Y-%m-%d"),
            "source": "akshare 公开数据",
            "total": len(data),
        },
        "data": data,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n💾 已保存: {OUTPUT_FILE} ({len(data)} 条)")
    return output


def main():
    use_sample = "--sample" in sys.argv

    if use_sample:
        print("📁 使用示例数据模式")
        data = fetch_data_sample()
    else:
        data = fetch_data_real()

    if not data:
        print("❌ 没有获取到任何数据")
        sys.exit(1)

    save_data(data)
    print("✅ 完成")


if __name__ == "__main__":
    main()
