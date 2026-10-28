#!/usr/bin/env python3
"""Examine official/public free-demo launch flows without a third-party relay.
Only accesses pages that explicitly advertise free demos; no wagering or authentication bypass.
Sanitizes URLs before saving: cookies, auth headers, token values are never exported.
"""
import asyncio, json, re, os, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from playwright.async_api import async_playwright

OUT=Path("results/public_launch")
OUT.mkdir(parents=True,exist_ok=True)
TARGETS=[
 {"name":"Dark Summoning", "source":"official-control", "url":"https://www.hacksawgaming.com/games/dark-summoning"},
 {"name":"Hellmageddon", "source":"dgn-public-demo", "url":"https://dgnzone.com/demos/hellmageddon"},
 {"name":"Ghost Vision", "source":"dgn-public-demo", "url":"https://dgnzone.com/demos/ghost-vision"},
 {"name":"Buried by Night", "source":"dgn-public-demo", "url":"https://dgnzone.com/demos/buried-by-night"}
]
SENSITIVE=re.compile(r"(token|auth|secret|session|sig|password|bearer|jwt|key|player|user|account|hash|nonce|cookie|ticket|credential)",re.I)
REDACT_TEXT=re.compile(r"(token|session|authorization|api-key|cookie|password|secret)=([^&\s'\"\]\}]+)",re.I)
def clean_url(url):
 try:
  p=urlsplit(url)
  if p.scheme not in ("http","https"):return ""
  query=[(k,"[REDACTED]" if SENSITIVE.search(k) else v[:70]) for k,v in parse_qsl(p.query,keep_blank_values=True)]
  return urlunsplit((p.scheme,p.netloc,p.path,urlencode(query),""))[:900]
 except:return ""
def clean_log(text):
 return REDACT_TEXT.sub(lambda m:m.group(1)+"=[REDACTED]",str(text))[:350]

async def one(browser,item):
 ctx=await browser.new_context(viewport={"width":1365,"height":850},locale="en-US",accept_downloads=False)
 page=await ctx.new_page()
 requests=[]
 console=[]
 opened=[]
 page.on("request",lambda r: requests.append({"type":r.resource_type,"method":r.method,"url":clean_url(r.url)}) if len(requests)<300 and
         (any(x in (urlsplit(r.url).hostname or "") for x in ("hacksaw","dgnzone","slot"))) else None)
 page.on("console",lambda m: console.append(clean_log(m.text)) if m.type=="error" and len(console)<20 else None)
 page.on("pageerror",lambda e: console.append("PAGEERROR "+clean_log(e)) if len(console)<20 else None)
 page.on("popup",lambda p:opened.append(p))
 result={"source":item["source"],"name":item["name"],"origin_page":item["url"],
         "navigation_status":None,"clicks":[],"frames_before":[],"frames_after":[],
         "external_resource_counts":{},"console_errors":[],"load_state":"unknown"}
 try:
  resp=await page.goto(item["url"],wait_until="domcontentloaded",timeout=45000)
  result["navigation_status"]=resp.status if resp else None
  await page.wait_for_timeout(3500)
  result["initial_title"]=(await page.title())[:120]
  result["frames_before"]=[clean_url(f.url) for f in page.frames]
  for label in ("Yes, I am over 18","Yes, I'm over 18","I am over 18","Accept All","Accept all"):
   try:
    loc=page.get_by_text(label,exact=False)
    if await loc.count() and await loc.first.is_visible():
     await loc.first.click(timeout=1800)
     result["clicks"].append("age/cookies: "+label)
     await page.wait_for_timeout(600)
     break
   except Exception:pass
  # Official Try it and publicly advertised third-party free demo buttons
  for selector in ("text=/^Try it$/i", "button:has-text('Play free demo')",
    "text=/^Play free demo$/i", "button:has-text('Play Demo')",
    "button:has-text('Play free')","a:has-text('Play free demo')"):
   try:
    matches=page.locator(selector)
    n=await matches.count()
    done=False
    for i in range(min(n,6)):
     loc=matches.nth(i)
     if await loc.is_visible():
      await loc.click(timeout=3500)
      result["clicks"].append("demo: "+selector)
      done=True
      break
    if done:break
   except Exception as e: result["clicks"].append("click-error: "+clean_log(e))
  await page.wait_for_timeout(10000)
  result["final_page_url"]=clean_url(page.url)
  result["final_title"]=(await page.title())[:140]
  result["frames_after"]=[clean_url(f.url) for f in page.frames]
  result["iframes"]=[clean_url(x) for x in (await page.locator("iframe").evaluate_all("(els)=>els.map(el=>el.src)"))][:15]
  result["popup_urls"]=[clean_url(p.url) for p in opened][:8]
  result["body_excerpt"]=(await page.locator("body").inner_text(timeout=5000))[:550]
  result["frame_details"]=[]
  for f in page.frames:
   try:
    result["frame_details"].append({"url":clean_url(f.url),"title":(await f.title())[:100],
      "body":(await f.locator("body").inner_text(timeout=1000))[:220] if await f.locator("body").count() else "",
      "canvas_count":await f.locator("canvas").count()})
   except Exception as e: result["frame_details"].append({"url":clean_url(f.url),"error":clean_log(e)})
  # Group request paths; keep no sensitive or game-session tokens
  interesting=[x for x in requests if x["type"] in ("document","xhr","fetch")]
  result["interesting_requests"]=interesting[:80]
  result["hacksaw_domains"]=sorted(set(urlsplit(x["url"]).hostname for x in requests if "hacksaw" in x["url"]))
  result["request_count"]=len(requests)
  screenshot= re.sub("[^a-z0-9]+","-",item["name"].lower()).strip("-")+".png"
  await page.screenshot(path=str(OUT/screenshot),full_page=False,timeout=10000)
  result["screenshot"]=screenshot
  all_text=" ".join((f.get("body") or "") for f in result["frame_details"])
  if "Connection lost to wallet" in all_text or "Connection lost to wallet" in result["body_excerpt"]:
   result["load_state"]="wallet_auth_failed"
  elif (any(f.get("canvas_count",0) for f in result["frame_details"]) and
       any("hacksawgaming.com" in f.get("url","") for f in result["frame_details"])):
   result["load_state"]="public_demo_canvas_loaded_check_manually"
  elif result["clicks"]:result["load_state"]="clicked_but_client_not_confirmed"
  else:result["load_state"]="public_demo_control_not_found"
 except Exception as e:
  result["error"]=clean_log(e)
  result["load_state"]="exception"
 finally:
  result["console_errors"]=console
  await ctx.close()
 return result
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--disable-dev-shm-usage","--no-sandbox"])
  sem=asyncio.Semaphore(2)
  async def wrapped(item):
   async with sem:
    print("Opening",item["source"],item["name"],flush=True)
    r=await one(browser,item)
    print("RESULT",r["name"],r["load_state"],"frames",len(r["frames_after"]), "hosts",r.get("hacksaw_domains"),flush=True)
    return r
  results=await asyncio.gather(*(wrapped(item) for item in TARGETS))
  await browser.close()
 payload={"tested_at_utc":datetime.now(timezone.utc).isoformat(),
   "privacy":"Sensitive query parameters redacted. No cookies, headers, or tokens exported.",
   "conclusion_limit":"A canvas or HTTP 200 does not certify successful demo authorization or spin.",
   "results":results}
 (OUT/"evidence.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Wrote",OUT/"evidence.json",flush=True)
if __name__=="__main__":asyncio.run(main())
