#!/usr/bin/env python3
"""Public BGaming official slots catalog collector, including SHOW MORE pagination.
No demo/game launch. No accounts or security checks bypassed.
"""
import asyncio,json,re,unicodedata
from pathlib import Path
from datetime import datetime,timezone
from playwright.async_api import async_playwright
OUT=Path("results/bgaming");OUT.mkdir(parents=True,exist_ok=True)
URL="https://bgaming.com/game-type/slots?types=slots"
JS=r"""() => {
const games=[...document.querySelectorAll('a[href]')].filter(a=>{
 try{const u=new URL(a.href);return u.hostname==='bgaming.com' && /^\/games\/[^/]+\/?$/.test(u.pathname)}catch{return false}
}).map(a=>{
 const box=a.closest('article,li,[class*=card],[class*=game],[class*=item]')||a.parentElement?.parentElement;
 return {url:a.href,raw:(box?.innerText||'').trim().slice(0,600)}
});
const more=[...document.querySelectorAll('button,[role=button],a')].filter(x=>
 /\bshow\s+more\b/i.test((x.textContent||'').trim()) && x.getBoundingClientRect().width>0)
 .map(x=>({tag:x.tagName,txt:(x.innerText||'').trim().slice(0,80),outer:x.outerHTML.slice(0,350)}));
return {games,more,tail:document.body.innerText.slice(-350)}
}"""
def pick(raw,url):
 lines=[re.sub(r"\s+"," ",x).strip() for x in raw.splitlines() if x.strip()]
 ix=next((i for i,s in enumerate(lines) if s.lower()=="slots"),None)
 if ix is not None and ix>0:return lines[ix-1]
 return url.split("/games/")[-1].strip("/").replace("-"," ").title()
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  ctx=await browser.new_context(viewport={"width":1400,"height":960},locale="en-US")
  page=await ctx.new_page()
  r=await page.goto(URL,wait_until="domcontentloaded",timeout=40000)
  await page.wait_for_timeout(1800)
  actions=[]
  for sel in ('text=/YES, I.M 18 YEARS OR OLDER/i','text=/^Accept all$/i'):
   try:
    b=page.locator(sel)
    if await b.count() and await b.last.is_visible():
     await b.last.click(timeout=1500)
     actions.append("accepted public age or cookies")
   except Exception:pass
  found={};rounds=[];stale=0
  for i in range(100):
   await page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
   await page.wait_for_timeout(500)
   data=await page.evaluate(JS)
   old=len(found)
   for g in data["games"]:found.setdefault(g["url"],g)
   if len(found)==old:stale+=1
   else:stale=0
   clicked=False;err=""
   for sel in ('text=/^SHOW MORE$/i','button:has-text("SHOW MORE")','[role=button]:has-text("SHOW MORE")'):
    try:
     loc=page.locator(sel)
     for k in range(min(3,await loc.count())):
      if await loc.nth(k).is_visible():
       await loc.nth(k).scroll_into_view_if_needed(timeout=1400)
       await loc.nth(k).click(timeout=2500)
       clicked=True
       break
     if clicked:break
    except Exception as e:err=str(e)[:95]
   rounds.append({"round":i,"found":len(found),"clicked":clicked,"more":data["more"][:2],"click_error":err})
   if i%5==0:print("ROUND",i,"found",len(found),"clicked",clicked,"stale",stale,flush=True)
   if not clicked and stale>=5:break
   if clicked:await page.wait_for_timeout(800)
  rows=[]
  for g in found.values():
   name=pick(g["raw"],g["url"])
   if name and name.lower() not in ("slots","play demo","details"):
    rows.append({"name":name,"url":g["url"],
       "demo_button_visible":"PLAY DEMO" in g["raw"].upper(),
       "card_text":g["raw"][:180]})
  out={"fetched_at_utc":datetime.now(timezone.utc).isoformat(),"source":URL,
       "page_http_status":r.status if r else None,
       "count":len(rows),"age_clicks":actions,"items":rows,"pagination_rounds":rounds,
       "warning":"Count equals encountered public cards only; includes announced titles shown by BGaming."}
  (OUT/"official_slots.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
  print("OFFICIAL SUMMARY",json.dumps({"count":len(rows),"last":rounds[-3:],"preview":rows[:5]},ensure_ascii=False),flush=True)
  await ctx.close();await browser.close()
if __name__=="__main__":asyncio.run(main())
