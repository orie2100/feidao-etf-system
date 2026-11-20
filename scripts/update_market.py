import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import akshare as ak
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/etfs.json'; OUT=ROOT/'data/market.json'
def num(v):
    try:
        x=float(v); return x if x==x else None
    except (TypeError,ValueError): return None
def previous():
    try: return json.loads(OUT.read_text(encoding='utf-8'))
    except Exception: return {'items':[]}
def fetch(x):
    df=ak.fund_etf_hist_em(symbol=x['code'],period='daily',start_date='19900101',end_date=datetime.now().strftime('%Y%m%d'),adjust='')
    if df is None or df.empty: raise RuntimeError('上游返回空数据')
    df=df.sort_values('日期'); last=df.iloc[-1]
    close=num(last.get('收盘'))
    if close is None: raise RuntimeError('最新收盘价缺失')
    prev=num(df.iloc[-2].get('收盘')) if len(df)>1 else None
    return {'code':x['code'],'name':x['name'],'sector':x.get('sector',''),'date':str(last.get('日期')),'close':close,'prev_close':prev,'change_pct':((close/prev)-1)*100 if prev else None,'high':num(df['最高'].max()),'low':num(df['最低'].min()),'amount':num(last.get('成交额')),'strategy_base_high':num(x.get('strategy_base_high')),'strategy_base_source':x.get('strategy_base_source',''),'price_basis':'未复权','status':'ok','error':None}
def main():
    cfg=json.loads(CONFIG.read_text(encoding='utf-8')); old={i.get('code'):i for i in previous().get('items',[])}; items=[]; ok=0
    for x in cfg:
        result=None; err=''
        for n in range(3):
            try: result=fetch(x); ok+=1; break
            except Exception as e: err=f'{type(e).__name__}: {e}'; time.sleep(2+n*3)
        if result is None:
            if x['code'] in old:
                result=dict(old[x['code']]); result.update(status='stale',error=err)
            else:
                result={'code':x['code'],'name':x['name'],'sector':x.get('sector',''),'strategy_base_high':num(x.get('strategy_base_high')),'status':'error','error':err,'price_basis':'未复权'}
        items.append(result); time.sleep(1)
    now=datetime.now(ZoneInfo('Asia/Shanghai'))
    data={'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),'generated_at_beijing':now.isoformat(),'source':'AKShare fund_etf_hist_em / Eastmoney','frequency':'daily_after_close','price_basis':'未复权','success_count':ok,'total_count':len(items),'items':items}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'更新成功 {ok}/{len(items)}')
    if ok==0: sys.exit(1)
if __name__=='__main__': main()
