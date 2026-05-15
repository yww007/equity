import json

DEFAULT_DATA = [
    {"rank":1,"name":"贵州茅台","code":"600519.SH","exchange":"sh","price":1820.50,"pe":28.6,"pb":9.2,"peg":1.42,"roe":32.5,"gross_margin":91.8,"net_margin":52.3,"stock_price":18.5,"cashflow":72.3,"net_profit_growth":0,"revenue_growth":0,"industry":"食品饮料"},
    {"rank":2,"name":"宁德时代","code":"300750.SZ","exchange":"sz","price":218.30,"pe":22.4,"pb":4.8,"peg":0.85,"roe":21.6,"gross_margin":24.3,"net_margin":12.8,"stock_price":62.8,"cashflow":32.5,"net_profit_growth":35.2,"revenue_growth":82.6,"industry":"电力设备"},
    {"rank":3,"name":"招商银行","code":"600036.SH","exchange":"sh","price":36.80,"pe":6.2,"pb":0.9,"peg":0.52,"roe":16.8,"gross_margin":42.5,"net_margin":32.8,"stock_price":88.5,"cashflow":85.2,"net_profit_growth":8.5,"revenue_growth":6.2,"industry":"银行"},
    {"rank":4,"name":"中国平安","code":"601318.SH","exchange":"sh","price":42.50,"pe":8.2,"pb":1.1,"peg":0.45,"roe":13.6,"gross_margin":18.5,"net_margin":11.2,"stock_price":62.8,"cashflow":95.8,"net_profit_growth":5.2,"revenue_growth":3.8,"industry":"非银金融"},
    {"rank":5,"name":"美的集团","code":"000333.SZ","exchange":"sz","price":62.80,"pe":13.5,"pb":2.8,"peg":0.92,"roe":22.5,"gross_margin":28.6,"net_margin":9.2,"stock_price":58.2,"cashflow":28.5,"net_profit_growth":12.8,"revenue_growth":8.5,"industry":"家用电器"},
    {"rank":6,"name":"恒瑞医药","code":"600276.SH","exchange":"sh","price":45.20,"pe":38.5,"pb":6.8,"peg":1.85,"roe":18.2,"gross_margin":82.5,"net_margin":22.6,"stock_price":8.5,"cashflow":18.5,"net_profit_growth":5.8,"revenue_growth":12.5,"industry":"医药"},
    {"rank":7,"name":"立讯精密","code":"002475.SZ","exchange":"sz","price":32.50,"pe":25.6,"pb":5.2,"peg":1.35,"roe":20.8,"gross_margin":12.5,"net_margin":6.8,"stock_price":42.5,"cashflow":12.8,"net_profit_growth":28.5,"revenue_growth":35.2,"industry":"电子"},
    {"rank":8,"name":"中兴通讯","code":"000063.SZ","exchange":"sz","price":28.80,"pe":18.5,"pb":3.2,"peg":0.75,"roe":15.6,"gross_margin":38.5,"net_margin":5.8,"stock_price":52.8,"cashflow":8.5,"net_profit_growth":42.5,"revenue_growth":28.6,"industry":"通信"},
    {"rank":9,"name":"三一重工","code":"600031.SH","exchange":"sh","price":16.80,"pe":22.8,"pb":2.5,"peg":1.25,"roe":11.2,"gross_margin":28.5,"net_margin":8.5,"stock_price":48.5,"cashflow":22.6,"net_profit_growth":15.2,"revenue_growth":18.5,"industry":"机械设备"},
    {"rank":10,"name":"紫金矿业","code":"601899.SH","exchange":"sh","price":14.50,"pe":16.8,"pb":3.5,"peg":0.68,"roe":19.8,"gross_margin":15.2,"net_margin":8.2,"stock_price":52.5,"cashflow":35.8,"net_profit_growth":25.6,"revenue_growth":22.8,"industry":"有色金属"},
    {"rank":11,"name":"海螺水泥","code":"600585.SH","exchange":"sh","price":26.80,"pe":10.2,"pb":1.5,"peg":0.55,"roe":14.2,"gross_margin":28.6,"net_margin":18.5,"stock_price":22.5,"cashflow":42.8,"net_profit_growth":-12.5,"revenue_growth":-8.5,"industry":"建筑材料"},
    {"rank":12,"name":"中国建筑","code":"601668.SH","exchange":"sh","price":5.82,"pe":4.8,"pb":0.7,"peg":0.38,"roe":13.8,"gross_margin":11.5,"net_margin":4.5,"stock_price":72.5,"cashflow":85.6,"net_profit_growth":6.8,"revenue_growth":8.5,"industry":"建筑装饰"},
    {"rank":13,"name":"万华化学","code":"600309.SH","exchange":"sh","price":88.50,"pe":15.8,"pb":3.2,"peg":0.82,"roe":22.8,"gross_margin":24.5,"net_margin":15.8,"stock_price":48.5,"cashflow":32.6,"net_profit_growth":18.5,"revenue_growth":15.2,"industry":"化工"},
    {"rank":14,"name":"比亚迪","code":"002594.SZ","exchange":"sz","price":268.50,"pe":32.5,"pb":6.5,"peg":1.15,"roe":18.5,"gross_margin":18.5,"net_margin":5.2,"stock_price":68.5,"cashflow":45.8,"net_profit_growth":52.8,"revenue_growth":42.5,"industry":"汽车"},
    {"rank":15,"name":"科大讯飞","code":"002230.SZ","exchange":"sz","price":42.80,"pe":55.6,"pb":5.8,"peg":2.35,"roe":8.5,"gross_margin":42.6,"net_margin":8.5,"stock_price":28.5,"cashflow":6.5,"net_profit_growth":15.8,"revenue_growth":22.6,"industry":"计算机"},
    {"rank":16,"name":"海尔智家","code":"600690.SH","exchange":"sh","price":28.50,"pe":14.2,"pb":2.8,"peg":0.88,"roe":20.5,"gross_margin":32.5,"net_margin":7.8,"stock_price":55.6,"cashflow":32.8,"net_profit_growth":18.5,"revenue_growth":12.8,"industry":"家用电器"},
    {"rank":17,"name":"中国中免","code":"601888.SH","exchange":"sh","price":82.50,"pe":28.5,"pb":5.2,"peg":1.45,"roe":18.8,"gross_margin":32.8,"net_margin":15.5,"stock_price":22.5,"cashflow":25.8,"net_profit_growth":8.5,"revenue_growth":12.5,"industry":"商贸零售"},
    {"rank":18,"name":"迈瑞医疗","code":"300760.SZ","exchange":"sz","price":285.60,"pe":32.8,"pb":8.5,"peg":1.55,"roe":28.5,"gross_margin":65.8,"net_margin":32.5,"stock_price":15.5,"cashflow":38.5,"net_profit_growth":18.5,"revenue_growth":15.8,"industry":"医药"},
    {"rank":19,"name":"中信证券","code":"600030.SH","exchange":"sh","price":22.80,"pe":15.8,"pb":1.5,"peg":0.95,"roe":9.8,"gross_margin":42.5,"net_margin":32.8,"stock_price":78.5,"cashflow":38.5,"net_profit_growth":12.5,"revenue_growth":8.5,"industry":"非银金融"},
    {"rank":20,"name":"药明康德","code":"603259.SH","exchange":"sh","price":68.50,"pe":38.5,"pb":5.2,"peg":1.65,"roe":15.8,"gross_margin":42.5,"net_margin":22.5,"stock_price":22.5,"cashflow":18.5,"net_profit_growth":25.6,"revenue_growth":32.5,"industry":"医药"},
    {"rank":21,"name":"工业富联","code":"601138.SH","exchange":"sh","price":18.50,"pe":18.5,"pb":3.2,"peg":0.85,"roe":16.8,"gross_margin":8.5,"net_margin":4.5,"stock_price":48.5,"cashflow":12.8,"net_profit_growth":32.5,"revenue_growth":28.5,"industry":"电子"},
    {"rank":22,"name":"伊利股份","code":"600887.SH","exchange":"sh","price":28.80,"pe":18.5,"pb":4.2,"peg":1.25,"roe":22.8,"gross_margin":32.5,"net_margin":9.5,"stock_price":52.5,"cashflow":38.5,"net_profit_growth":8.5,"revenue_growth":6.8,"industry":"食品饮料"},
    {"rank":23,"name":"海康威视","code":"002415.SZ","exchange":"sz","price":35.80,"pe":22.5,"pb":4.8,"peg":1.55,"roe":21.5,"gross_margin":45.8,"net_margin":22.5,"stock_price":35.6,"cashflow":25.8,"net_profit_growth":8.5,"revenue_growth":6.5,"industry":"计算机"},
    {"rank":24,"name":"中芯国际","code":"688981.SH","exchange":"sh","price":56.20,"pe":52.8,"pb":3.8,"peg":2.85,"roe":6.8,"gross_margin":22.6,"net_margin":12.5,"stock_price":18.5,"cashflow":8.2,"net_profit_growth":0,"revenue_growth":0,"industry":"电子"},
    {"rank":25,"name":"中国联通","code":"600941.SH","exchange":"sh","price":5.28,"pe":18.5,"pb":1.2,"peg":1.15,"roe":6.8,"gross_margin":28.5,"net_margin":5.8,"stock_price":38.6,"cashflow":28.6,"net_profit_growth":0,"revenue_growth":0,"industry":"通信"},
]

params = [
    {'key': 'pe', 'low': True},
    {'key': 'pb', 'low': True},
    {'key': 'peg', 'low': True},
    {'key': 'roe', 'low': False},
    {'key': 'gross_margin', 'low': False},
    {'key': 'net_margin', 'low': False},
    {'key': 'debt_ratio', 'low': True},
    {'key': 'cashflow', 'low': False},
    {'key': 'net_profit_growth', 'low': False},
    {'key': 'revenue_growth', 'low': False},
]

# Compute top3ByCol as JS does
top3ByCol = {}
for p in params:
    sorted_data = sorted(DEFAULT_DATA, key=lambda x: x[p['key']] or 0, reverse=not p['low'])
    top3 = {}
    for i, item in enumerate(sorted_data[:3]):
        top3[item['code']] = 'cell-top-' + str(i + 1)
    top3ByCol[p['key']] = top3

print("=== 各参数前三名 ===")
for k, v in top3ByCol.items():
    print(f"{k}: {v}")

print("\n=== 前15行匹配情况 ===")
for idx, item in enumerate(DEFAULT_DATA[:15]):
    print(f"\n行{idx+1}: {item['name']} ({item['code']})")
    for p in params:
        topIdx = top3ByCol[p['key']].get(item['code'], None)
        status = f"✓ {topIdx}" if topIdx else "✗"
        print(f"  {p['key']}: {status}")
