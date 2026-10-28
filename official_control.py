#!/usr/bin/env python3
"""Inspect official Hacksaw 'Try it' demo navigation with consent handling.
No account use, no bets, no auth bypass, no session material in results.
"""
import asyncio, json, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from playwright.async_api import async_playwright
OUT=Path("results/official_control")
OUT.mkdir(parents=True,exist_ok=True)
GAMES={"dark-summoning":"Dark Summoning","le-bandit":"Le Bandit"}
def sanitize(url):
 try:
  p=urlsplit(url)
  q=[(k,("***" if re.search(r'token|auth|key|session|secret|sig|cookie|jwt|user|player',k,re.I) else v[:100])) for k,v in parse_qsl(p.query,keep_blank_values=True)]
  return urlunsplit((p.scheme,p.netloc,p.path,urlencode(q),""))[:1200]
 except:return ""
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True,args=["--disable-dev-shm-usage","--no-sandbox"])
  results=[]
  for slug,name in GAMES.items():
   ctx=await b.new_context(viewport={"width":1365,"height":850},locale="en-US")
   page=await ctx.new_page()
   reqs=[]
   page.on("request",lambda r:reqs.append({"type":r.resource_type,"url":sanitize(r.url)}) if r.resource_type in ("document","xhr","fetch") and len(reqs)<150 else None)
   res={"game":name,"official":f"https://www.hacksawgaming.com/games/{slug}","actions":[]}
   try:
    await page.goto(res["official"],wait_until="domcontentloaded",timeout=40000)
    await page.wait_for_timeout(2500)
    res["initial_buttons"]=(await page.locator("button").all_inner_texts())[:40]
    res["initial_frames"]=[sanitize(f.url) for f in page.frames]
    await page.screenshot(path=str(OUT/f"{slug}-before.png"))
    # Public cookie consent dialog; fixed coordinates correspond to the observed desktop viewport.
    # Check dialog with DOM first, then click its visible "OK" control using explicit coordinates.
    clicked=False
    for sel in ("button:has-text('OK')","text=/^OK$/i","input[value='OK']",
                "[aria-label='OK']"):
     try:
      loc=page.locator(sel)
      for k in range(min(5,await loc.count())):
       if await loc.nth(k).is_visible():
        await loc.nth(k).click(timeout=1300)
        res["actions"].append("consent via "+sel)
        clicked=True
        break
      if clicked:break
     except Exception as e: res["actions"].append("failed "+sel+":"+str(e)[:75])
    if not clicked:
     await page.mouse.click(620,478)
     res["actions"].append("consent fallback click (620,478)")
    await page.wait_for_timeout(1300)
    await page.screenshot(path=str(OUT/f"{slug}-after-consent.png"))
    res["after_consent_buttons"]=(await page.locator("button").all_inner_texts())[:40]
    click=False
    for sel in ("text=/^Try it$/i","a:has-text('Try it')","button:has-text('TRY IT')"):
     try:
      t=page.locator(sel)
      for i in range(min(await t.count(),5)):
       if await t.nth(i).is_visible():
        await t.nth(i).click(timeout=2200)
        res["actions"].append("try it via "+sel)
        click=True
        break
      if click:break
     except Exception as e:res["actions"].append("failed tryit:"+str(e)[:75])
    if not click:
     await page.mouse.click(1168,472)
     res["actions"].append("try it fallback click (1168,472)")
    await page.wait_for_timeout(2200)
    await page.screenshot(path=str(OUT/f"{slug}-post-tryit.png"))
    for sel in ("text=/Yes, I am over 18/i","button:has-text('I am over 18')",
                "button:has-text('YES')"):
     try:
      t=page.locator(sel)
      if await t.count() and await t.first.is_visible():
       await t.first.click(timeout=1500)
       res["actions"].append("age confirmation via "+sel)
       break
     except Exception:pass
    await page.wait_for_timeout(9000)
    await page.screenshot(path=str(OUT/f"{slug}-final.png"))
    res["frames_after"]=[sanitize(f.url) for f in page.frames]
    res["popup_count"]=len(ctx.pages)-1
    res["popups"]=[sanitize(x.url) for x in ctx.pages[1:]]
    res["frame_details"]=[]
    for f in page.frames:
     try:
      res["frame_details"].append({"url":sanitize(f.url),"title":(await f.title())[:130],
         "body":(await f.locator("body").inner_text(timeout=1400))[:180] if await f.locator("body").count() else "",
         "canvas":await f.locator("canvas").count()})
     except:pass
    res["requests"]=reqs
    res["final_buttons"]=(await page.locator("button").all_inner_texts())[:35]
    res["final_text"]=(await page.locator("body").inner_text())[:500]
   except Exception as e:res["error"]=str(e)[:280]
   print(json.dumps({"game":name,"actions":res["actions"],"frames":res.get("frames_after"),"popups":res.get("popups"),"error":res.get("error")}),flush=True)
   results.append(res)
   await ctx.close()
  await b.close()
  (OUT/"evidence.json").write_text(json.dumps({"checked_at_utc":datetime.now(timezone.utc).isoformat(),"results":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":asyncio.run(main())
