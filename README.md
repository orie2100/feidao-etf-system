# 飞刀ETF智能分析系统 V1.1

## 功能
- 工作日北京时间18:25由GitHub Actions触发行情更新（UTC 10:25）。
- Python + AKShare `fund_etf_hist_em` 获取ETF日线历史行情，生成 `data/market.json`。
- 手机端静态页面读取JSON，展示收盘价、日涨跌、历史高低点、五阶档位及最低点×3禁买线。
- 失败时标记旧数据/失败，不伪造实时价格。

## 策略口径（依据《瑞宇飞刀ETF策略—完整执行手册》）
- 第4页五阶：1.0–0.8、0.8–0.6、0.6–0.4、0.4–0.3、0.3以下。
- 第5页长线建仓正文：0.40/0.35/0.30，投入长线预算20%/30%/50%。附录A的0.420/0.3530/0.3050与正文不一致，本版按正文。
- 网格：每跌5%买一格；对应买入后上涨10%为卖出参考价。
- 致敬仓：跌破0.3后，每再跌1%投入致敬仓预算10%。
- 防追高：当前价≥历史最低价×3，禁止新增买入。该条件独立于五阶档位。
- `strategy_base_high` 必须人工确认，不能擅自把每只ETF的历史最高价等同于策略“1元基准”。
- 当前行情使用未复权日线，现价/历史高低点同口径。分红、份额折算等可能影响连续性，正式使用前须确认该口径。

## 上传 GitHub
1. 新建仓库（如 `feidao-etf-system`），解压本包后将文件全部上传至仓库根目录并提交到 `main`。
2. GitHub仓库 Settings → Actions → General，允许Actions运行；进入Actions启用 `Daily ETF Market Update`，可先手动运行一次。
3. 检查 `data/market.json` 是否更新。

## Cloudflare Pages
1. Cloudflare Dashboard → Workers & Pages → Create application → Pages → Connect to Git。
2. 选择GitHub仓库；Production branch=`main`；Build command=`exit 0`；Build output directory=`/`。
3. 部署完成后手机浏览器访问 `*.pages.dev` 地址，可添加到主屏幕。

## 修改观察列表
编辑 `config/etfs.json`。`strategy_base_high` 初始留空，须根据策略基准人工确认后填写。

## 本地运行
```bash
pip install -r requirements.txt
python scripts/update_market.py
```

## 限制
- 这是日线收盘数据，不是盘中实时行情；当日行情通常需收盘后才能完整取得。
- AKShare上游接口可能失败；当前实现重试，单只失败标旧数据/失败，全部失败则Actions失败。
- 新浪备用源暂未启用，需先验证字段和价格口径，不能与主源未经校验混用。
- 暂未计算10/20月线、MACD、PE/PB分位、折溢价率、年化波动率和最大回撤。
- 不下单、不连接券商、不保证收益。免费服务与定时任务可能变化或延迟。
