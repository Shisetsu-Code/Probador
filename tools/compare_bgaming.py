#!/usr/bin/env python3
"""Extract and contrast publicly listed BGaming titles. No demo launches."""
import asyncio,csv,json,re,unicodedata
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
from playwright.async_api import async_playwright

OUT=Path("results/bgaming");OUT.mkdir(parents=True,exist_ok=True)
SOURCES={"choice":"https://choicecasino.com/es/games/bgaming/slots",
 "slotcatalog":"https://slotcatalog.com/es/soft/BGAMING",
 "official":"https://bgaming.com/game-type/slots?types=slots"}
def norm(s):
 s=unicodedata.normalize("NFKD",str(s)).lower()
 s="".join(c for c in s if not unicodedata.combining(c))
 s=s.replace("™","").replace("®","").replace("&","and")
 return re.sub("[^a-z0-9]+","",s)
def nice(s):return re.sub(r"\s+"," ",str(s or "")).strip()[:160]
async def visit(page,url):
 try:
  r=await page.goto(url,wait_until="domcontentloaded",timeout=30000)
  await page.wait_for_timeout(1100)
  return {"status":r.status if r else None,"url":page.url}
 except Exception as e:return {"error":str(e)[:180],"url":url}

async def choice(browser):
 ctx=await browser.new_context(locale="es-ES")
 page=await ctx.new_page();nav=await visit(page,SOURCES["choice"])
 body=await page.locator("body").inner_text()
 seg=body.split("Slots de BGAMING",1)[-1].split("Casinos en países",1)[0]
 lines=[nice(s) for s in seg.splitlines() if nice(s)]
 names=[]
 for i,line in enumerate(lines):
  if line.upper()=="BGAMING" and i:
   n=lines[i-1]
   if n not in ("BGAMING","Slots") and not n.startswith("Todas las"):names.append(n)
 dom=await page.evaluate("""() => ({
  pagination:[...document.querySelectorAll('a[href]')].filter(a=>/[?&](page|p)=\\d+|\\/slots\\/\\d+$/.test(a.href)).map(a=>({text:a.innerText,href:a.href})).slice(0,15),
  links:[...document.querySelectorAll('a[href]')].filter(a=>/\\/games\\//.test(a.href)).map(a=>({text:a.innerText.slice(0,60),href:a.href})).slice(-20),
  tail:document.body.innerText.slice(-700)
 })""")
 await ctx.close()
 return [{"name":n,"source":"choice","url":""} for n in dict.fromkeys(names)],{"nav":nav,"detected":len(names),"head":seg[:450],"tail":seg[-500:],"dom":dom}

async def slot_page(browser,i,sem):
 async with sem:
  ctx=await browser.new_context(locale="es-ES")
  page=await ctx.new_page()
  url=SOURCES["slotcatalog"]+(("/"+str(i)) if i>1 else "")
  nav=await visit(page,url)
  dom=await page.evaluate("""() => ({
   gameLinks:[...document.querySelectorAll('a[href]')].filter(a=>/\\/slots\\//i.test(a.href))
      .map(a=>({name:(a.innerText||a.textContent||'').trim(),href:a.href,alt:a.querySelector('img')?.alt||''})).slice(0,100),
   body:document.body.innerText.slice(0,10000)
  })""")
  await ctx.close()
  listing=dom["body"]
  if "Ordenando" in listing:listing=listing.split("Ordenando",1)[-1]
  if "Elementos:" in listing:listing=listing.split("Elementos:",1)[0]
  links=[]
  for a in dom["gameLinks"]:
   n=nice(a["name"]).removeprefix("Detalles ")
   if n and len(n)>2 and not re.match(r"^(Detalles|Ir al casino|Play|Casino|\\d+)$",n,re.I):
    links.append({"name":n,"url":a["href"],"source":"slotcatalog"})
  # Rendered listing contains repeating name immediately after Detalles
  if not links:
   for m in re.finditer(r"Detalles\s+([^\n]+)",listing):
    n=nice(m.group(1))
    if n and not n.isdigit() and len(n)>2:links.append({"name":n,"url":"","source":"slotcatalog"})
  distinct={}
  for x in links:distinct.setdefault(norm(x["name"]),x)
  return list(distinct.values()),{"page":i,"count":len(distinct),"nav":nav,
    "body_excerpt":listing[:900],"links_sample":dom["gameLinks"][:5]}

async def slotcatalog(browser):
 sem=asyncio.Semaphore(5)
 results=await asyncio.gather(*(slot_page(browser,i,sem) for i in range(1,35)))
 rows={};diag=[]
 for games,d in results:
  diag.append(d)
  for x in games:rows.setdefault(norm(x["name"]),x)
 return list(rows.values()),{"total":len(rows),"pages":diag}

async def official(browser):
 ctx=await browser.new_context(viewport={"width":1400,"height":900},locale="en-GB")
 page=await ctx.new_page()
 nav=await visit(page,SOURCES["official"])
 await page.wait_for_timeout(1300)
 js="""() => {
 const anchors=[...document.querySelectorAll('a[href]')];
 const games=anchors.filter(a=>{try {let u=new URL(a.href);return u.hostname==='bgaming.com' && /^\\/games\\/[^/]+\\/?$/.test(u.pathname)}catch{return false}})
 .map(a=>{
  const el=a.closest('article,li,[class*=card],[class*=game],[class*=item]');
  const parent=el||a.parentElement?.parentElement;
  const raw=parent?.innerText||'';
  return {name:(parent?.querySelector('h2,h3,h4')?.innerText||a.innerText||'').trim(),url:a.href,raw:raw.slice(0,350)}
 });
 const buttons=[...document.querySelectorAll('button,[role=button]')].map(x=>({
  text:(x.innerText||x.getAttribute('aria-label')||'').trim().slice(0,80),
  visible:!!(x.getBoundingClientRect().width&&x.getBoundingClientRect().height)}));
 return {games,buttons,tail:document.body.innerText.slice(-900)}
}"""
 games={};diagnostics=[];stale=0
 for i in range(60):
  await page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
  await page.wait_for_timeout(500)
  d=await page.evaluate(js)
  prior=len(games)
  for x in d["games"]:games.setdefault(x["url"],x)
  stale=stale+1 if len(games)==prior else 0
  clicked=False
  for selector in ("button:has-text('Load More')","button:has-text('Load more')",
                   "button:has-text('Show more')","text=/^Load more$/i"):
   try:
    el=page.locator(selector)
    if await el.count() and await el.last.is_visible():
     await el.last.click(timeout=1600);clicked=True;break
   except Exception:pass
  diagnostics.append({"round":i,"games":len(games),"clicked":clicked,
    "buttons":[b["text"] for b in d["buttons"] if b["visible"] and re.search("load|more|next",b["text"],re.I)][:10]})
  if not clicked and stale>=7:break
  if clicked:await page.wait_for_timeout(500)
 end=await page.evaluate(js)
 await ctx.close()
 rows=[]
 for u,x in games.items():
  name=nice(x["name"])
  if not name or name.lower() in ("details","play demo","games","slots","play"):
   raw=x["raw"]
   name=nice(raw.split("\nSlots")[0].replace("Coming soon",""))
  if not name:name=u.rstrip("/").split("/")[-1].replace("-"," ").title()
  rows.append({"name":name,"url":u,"source":"official",
   "status":"coming_soon" if "coming soon" in x["raw"].lower() else "listed"})
 return rows,{"nav":nav,"count":len(rows),"sample":list(games.values())[:10],
   "rounds":diagnostics,"tail":end["tail"],"buttons":end["buttons"][-30:]}

def merge(result,diagnostics):
 allnames={}
 for src,games in result.items():
  for g in games:
   k=norm(g["name"])
   if not k:continue
   if k not in allnames:allnames[k]={"name":g["name"],"choice":"","slotcatalog":"","official":"",
     "choice_url":"","slotcatalog_url":"","official_url":"","official_status":""}
   item=allnames[k];item[src]="yes";item[src+"_url"]=g.get("url","")
   if src=="official":item["official_status"]=g.get("status","")
 rows=sorted(allnames.values(),key=lambda x:x["name"].lower())
 for row in rows:
  pres=[x for x in ("choice","slotcatalog","official") if row[x]]
  row["sources_count"]=len(pres);row["exclusive_to"]=pres[0] if len(pres)==1 else ""
 out={"collected_at_utc":datetime.now(timezone.utc).isoformat(),
  "source_urls":SOURCES,"counts_raw":{k:len(v) for k,v in result.items()},
  "union":len(rows),"all_three":sum(r["sources_count"]==3 for r in rows),
  "exclusive":{k:sum(r["exclusive_to"]==k for r in rows) for k in result},
  "warning":"Provider-wide SlotCatalog includes other game categories; official pages may include coming soon. Data quality and completeness depend on DOM extraction.",
  "games":rows}
 (OUT/"comparison.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 fields=["name","choice","slotcatalog","official","sources_count","exclusive_to",
         "choice_url","slotcatalog_url","official_url","official_status"]
 with (OUT/"comparison.csv").open("w",newline="",encoding="utf-8-sig") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 (OUT/"diagnostics.json").write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2)+"\n")
 print("COUNTS",json.dumps({k:v for k,v in out.items() if k!="games"},ensure_ascii=False),flush=True)

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  try:
   res=await asyncio.gather(choice(browser),slotcatalog(browser),official(browser))
   data={k:v[0] for k,v in zip(("choice","slotcatalog","official"),res)}
   debug={k:v[1] for k,v in zip(("choice","slotcatalog","official"),res)}
   for k,v in data.items():print("SOURCE",k,len(v),[x["name"] for x in v[:9]],flush=True)
   merge(data,debug)
  finally:await browser.close()
if __name__=="__main__":asyncio.run(main())
