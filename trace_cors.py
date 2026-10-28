#!/usr/bin/env python3
"""Read-only Chrome CORS diagnostic for the official public game demo.
Stores request METHOD and allowlisted preflight headers ONLY.
Does not capture request bodies, cookies, credentials, token values or authentication responses.
"""
import asyncio,json
from datetime import datetime,timezone
from pathlib import Path
from playwright.async_api import async_playwright
TARGET="https://www.hacksawgaming.com/games/dark-summoning"
def header(h,key):
 return next((v for k,v in h.items() if k.lower()==key.lower()),None)
def safe(event,info):
 req=event.get("request",{})
 headers=req.get("headers",{})
 return {"id":event.get("requestId"),"method":req.get("method"),"path":req.get("url","").split("?")[0],
    "origin":header(headers,"Origin"),
    "access_control_request_method":header(headers,"Access-Control-Request-Method"),
    "access_control_request_headers":header(headers,"Access-Control-Request-Headers"),
    "initiator_type":event.get("initiator",{}).get("type")}
async def main():
 out={"checked_at_utc":datetime.now(timezone.utc).isoformat(),"test":TARGET,"requests":[],"events":[],"observed":{}}
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  context=await browser.new_context(viewport={"width":1365,"height":850})
  page=await context.new_page()
  cdp=await context.new_cdp_session(page)
  await cdp.send("Network.enable")
  reqmap={}
  def onrequest(e):
   u=e.get("request",{}).get("url","")
   if "rgs-demo.hacksawgaming.com" not in u: return
   id=e.get("requestId")
   reqmap[id]=len(out["requests"])
   out["requests"].append(safe(e,{}))
  def onresponse(e):
   id=e.get("requestId")
   if id not in reqmap:return
   r=e.get("response",{})
   out["requests"][reqmap[id]].update({"response_status":r.get("status"),
      "response_origin":header(r.get("headers",{}),"access-control-allow-origin"),
      "response_methods":header(r.get("headers",{}),"access-control-allow-methods"),
      "response_headers":header(r.get("headers",{}),"access-control-allow-headers")})
  def onextra(e):
   id=e.get("requestId")
   if id not in reqmap:return
   out["requests"][reqmap[id]]["extra_status"]=e.get("statusCode")
   h=e.get("headers",{})
   out["requests"][reqmap[id]]["extra_origin"]=header(h,"access-control-allow-origin")
  def onfailed(e):
   id=e.get("requestId")
   if id not in reqmap:return
   out["requests"][reqmap[id]].update({"error":e.get("errorText"),
       "blocked_reason":e.get("blockedReason"),"cors_error":e.get("corsErrorStatus",{}).get("corsError")})
  cdp.on("Network.requestWillBeSent",onrequest)
  cdp.on("Network.responseReceived",onresponse)
  cdp.on("Network.responseReceivedExtraInfo",onextra)
  cdp.on("Network.loadingFailed",onfailed)
  try:
   resp=await page.goto(TARGET,wait_until="domcontentloaded",timeout=38000)
   out["observed"]["site_status"]=resp.status if resp else None
   await page.wait_for_timeout(1800)
   ck=page.get_by_role("button",name="OK",exact=True)
   if await ck.count() and await ck.first.is_visible():
    await ck.first.click(timeout=1800)
   else:await page.mouse.click(620,478)
   await page.wait_for_timeout(650)
   await page.locator("text=/^Try it$/i").first.click(timeout=3500)
   await page.wait_for_timeout(550)
   age=page.locator("text=/Yes, I am over 18/i")
   if await age.count() and await age.first.is_visible():
    await age.first.click(timeout=3500)
   await page.wait_for_timeout(11000)
   out["observed"]["frame_titles"]=[]
   for f in page.frames:
    try: out["observed"]["frame_titles"].append((await f.title())[:70])
    except:pass
   wallet_error=False
   for f in page.frames:
    try:
     if await f.locator("body").count() and "Connection lost to wallet" in (await f.locator("body").inner_text(timeout=1000)):
      wallet_error=True
    except Exception:pass
   out["observed"]["wallet_error"]=wallet_error
  except Exception as e:out["observed"]["error"]=str(e)[:250]
  finally:
   await context.close();await browser.close()
 Path("results").mkdir(exist_ok=True)
 Path("results/cors_trace.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":asyncio.run(main())
