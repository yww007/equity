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
    """使用 akshare 东方财富(EM)接口获取真实数据"""
    try:
        import akshare as ak
        import pandas as pd
    except ImportError:
        print("❌ 缺少依赖: pip install akshare pandas")
        sys.exit(1)

    results = []
    errors = []

    # 自动选择最新报告期
    today = datetime.now()
    y = today.year
    m = today.month
    if m >= 10:
        date_str = f"{y}0930"
    elif m >= 7:
        date_str = f"{y}0630"
    elif m >= 4:
        date_str = f"{y}0331"
    else:
        date_str = f"{y - 1}1231"

    print(f"📡 获取最新报告期({date_str})财务数据...")
    print("-" * 50)

    # 批量获取所有股票的财报数据（一次请求）
    try:
        yjbb = ak.stock_yjbb_em(date=date_str)
        # 如果为空则尝试前一报告期
        if yjbb.empty:
            fallback = {"10": "0630", "7": "0331", "4": f"{y-1}1231", "1": f"{y-1}0930"}
            fb_key = str(m)
            if fb_key in fallback:
                fb_date = fallback[fb_key]
            else:
                fb_date = f"{y-1}1231"
            if not fb_date.startswith(str(y)):
                fb_date = f"{y-1}1231"
            print(f"⚠ 报告期 {date_str} 无数据，尝试 {fb_date}")
            yjbb = ak.stock_yjbb_em(date=fb_date)
        print(f"✅ 获取到 {len(yjbb)} 只股票的财报数据")
    except Exception as e:
        print(f"❌ 获取财报失败: {e}")
        return []

    # 先加载上次保存的股价作为兜底（行情接口不可用时使用）
    fallback_price_map = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            for item in (old_data.get("data", old_data) if isinstance(old_data, dict) else old_data):
                if isinstance(item, dict) and "code" in item and item.get("stock_price", 0) > 0:
                    # code 格式为 "600519.SH"，提取前6位作为匹配键
                    code_key = item["code"].split(".")[0]
                    fallback_price_map[code_key] = item["stock_price"]
            if fallback_price_map:
                print(f"📦 已加载 {len(fallback_price_map)} 只股票的上次股价作为兜底")
        except Exception:
            pass

    # 批量获取所有股票实时行情（新浪接口），建立 code→price 映射
    print("📡 获取实时行情...")
    try:
        spot_df = ak.stock_zh_a_spot()
        # 新浪接口返回代码带 sh/sz/bj 前缀，去掉前缀以便匹配 STOCKS
        spot_df['_code'] = spot_df['代码'].str.replace(r'^(sh|sz|bj)', '', regex=True)
        price_map = dict(zip(spot_df['_code'], spot_df['最新价']))
        print(f"✅ 获取到 {len(price_map)} 只股票的实时行情")
    except Exception as e:
        print(f"❌ 获取实时行情失败: {e}")
        price_map = {}

    # 将兜底价格合并到 price_map（实时行情优先，缺失的用兜底）
    for code_key, fallback_price in fallback_price_map.items():
        curr = price_map.get(code_key, 0)
        if curr == 0 or (isinstance(curr, float) and pd.isna(curr)):
            price_map[code_key] = fallback_price
    if fallback_price_map:
        print(f"📊 最终可用股价数: {len([k for k, v in price_map.items() if v > 0])} 只")

    print(f"📡 开始整合 {len(STOCKS)} 只股票的数据...")
    print("-" * 50)

    for idx, (code, name) in enumerate(STOCKS, 1):
        try:
            exchange = get_exchange(code)
            full_code = f"{code}.{exchange.upper()}"

            print(f"  [{idx}/{len(STOCKS)}] {name} ({full_code}) ... ", end="", flush=True)

            # 从 yjbb 中找到该股票的财务数据
            stock_fin = yjbb[yjbb['股票代码'] == code]
            if stock_fin.empty:
                print("⚠ 无财务数据")
                continue

            fin_row = stock_fin.iloc[0]

            # 从 price_map 获取最新价
            price = price_map.get(code, 0)
            industry = fin_row.get("所处行业", "其他")

            # 提取财务数据
            eps = float(fin_row["每股收益"]) if pd.notna(fin_row.get("每股收益")) else 0
            bvps = float(fin_row["每股净资产"]) if pd.notna(fin_row.get("每股净资产")) else 0
            roe = float(fin_row["净资产收益率"]) if pd.notna(fin_row.get("净资产收益率")) else 0
            gross_margin = float(fin_row["销售毛利率"]) if pd.notna(fin_row.get("销售毛利率")) else 0
            net_profit = float(fin_row["净利润-净利润"]) if pd.notna(fin_row.get("净利润-净利润")) else 0
            revenue = float(fin_row["营业总收入-营业总收入"]) if pd.notna(fin_row.get("营业总收入-营业总收入")) else 0
            net_margin_pct = round(net_profit / revenue * 100, 1) if revenue else 0
            net_profit_growth = float(fin_row["净利润-同比增长"]) if pd.notna(fin_row.get("净利润-同比增长")) else 0
            revenue_growth = float(fin_row["营业总收入-同比增长"]) if pd.notna(fin_row.get("营业总收入-同比增长")) else 0
            cashflow_per_share = float(fin_row["每股经营现金流量"]) if pd.notna(fin_row.get("每股经营现金流量")) else 0

            # 计算 PE、PB
            pe = round(price / eps, 2) if eps > 0 else 0
            pb = round(price / bvps, 2) if bvps > 0 else 0
            peg = round(pe / roe * 100, 2) if roe > 0 and pe > 0 else 0

            results.append({
                "rank": idx,
                "name": name,
                "code": full_code,
                "exchange": exchange,
                "pe": pe,
                "pb": pb,
                "peg": peg,
                "roe": round(roe, 1),
                "gross_margin": round(gross_margin, 1),
                "net_margin": round(net_margin_pct, 1),
                "stock_price": price,  # 最新股价
                "cashflow": round(cashflow_per_share, 1),
                "net_profit_growth": round(net_profit_growth, 1),
                "revenue_growth": round(revenue_growth, 1),
                "industry": industry,
            })

            print(f"✅ PE={pe:.1f} ROE={roe:.1f}% 净利润增长={net_profit_growth:.1f}%")

            # 避免请求过快被封
            time.sleep(0.3)

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
    """保存数据到 JSON 文件并归档每日快照"""
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

    today = datetime.now().strftime("%Y-%m-%d")
    output = {
        "meta": {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data_date": today,
            "source": "akshare 公开数据",
            "total": len(data),
        },
        "data": data,
    }

    # 保存到 stocks.json（当前数据）
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存: {OUTPUT_FILE} ({len(data)} 条)")

    # 归档每日快照
    archive_dir = os.path.join(OUTPUT_DIR, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    archive_file = os.path.join(archive_dir, f"{today}.json")
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"📦 已归档: {archive_file}")

    # 更新归档索引 archive/index.json
    archive_index = []
    if os.path.exists(os.path.join(archive_dir, "index.json")):
        try:
            with open(os.path.join(archive_dir, "index.json"), "r", encoding="utf-8") as f:
                archive_index = json.load(f)
        except Exception:
            pass

    # 合并去重（按日期去重，已存在的日期更新 total）
    date_set = {entry["date"] for entry in archive_index if "date" in entry}
    if today in date_set:
        for entry in archive_index:
            if entry.get("date") == today:
                entry["total"] = len(data)
                break
    else:
        archive_index.append({
            "date": today,
            "total": len(data),
            "file": f"{today}.json",
        })
    archive_index.sort(key=lambda x: x["date"], reverse=True)

    with open(os.path.join(archive_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(archive_index, f, ensure_ascii=False, indent=2)
    print(f"📋 归档索引已更新 ({len(archive_index)} 个存档日)")

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
