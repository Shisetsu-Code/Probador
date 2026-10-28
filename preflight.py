#!/usr/bin/env python3
"""Read-only CORS preflight diagnostics of public Hacksaw demo backends.
No login, tokens, credentials, session, gameplay or POST requests.
"""
import json,ssl
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
TARGETS=[
 ("official-demo-auth","https://rgs-demo.hacksawgaming.com/api/play/authenticate","https://static-live.hacksawgaming.com","POST"),
 ("official-demo-settings","https://rgs-demo.hacksawgaming.com/api/play/partnerSettings","https://static-live.hacksawgaming.com","POST"),
 ("staging-demo-auth","https://rgs-hacksaw-fun-stg.hacksawgaming.com/api/play/authenticate","https://static-stg.hacksawgaming.com","POST"),
 ("staging-demo-settings","https://rgs-hacksaw-stg.hacksawgaming.com/api/play/partnerSettings","https://static-stg.hacksawgaming.com","POST")
]
def probe(label,url,origin,method):
 headers={"Origin":origin,"Access-Control-Request-Method":method,
 "Access-Control-Request-Headers":"content-type","User-Agent":"Mozilla/5.0 (compatible; Public-Demo-Diagnostics/1.0)"}
 row={"label":label,"url":url,"origin":origin,"intended_method":method,"status":None}
 try:
  req=Request(url,headers=headers,method="OPTIONS")
  try:
   response=urlopen(req,timeout=17)
  except HTTPError as e:
   response=e
  with response:
   row["status"]=response.status
   row["headers"]={k:response.headers.get(k) for k in (
    "access-control-allow-origin","access-control-allow-methods",
    "access-control-allow-headers","vary","server","cf-ray","content-type",
    "www-authenticate") if response.headers.get(k)}
 except Exception as e: row["network_error"]=type(e).__name__+": "+str(e)[:150]
 return row
def main():
 out={"checked_at_utc":datetime.now(timezone.utc).isoformat(),
      "purpose":"Compare official demo and staging browser CORS preflight, no authorization or gameplay bypass",
      "tests":[probe(*x) for x in TARGETS]}
 Path("results").mkdir(exist_ok=True)
 Path("results/backend_preflight.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
