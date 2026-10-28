# 通过各校 sitemap.xml 猜测项目页 URL（命中率约 20%，仅作线索）
import re, json, subprocess, sys, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
HTML = "index.html"   # 仓库根目录的页面文件

def get(url, t=12):
    r = subprocess.run(["curl","-sL","-m",str(t),"-A",UA,url], capture_output=True, text=True, errors="ignore")
    return r.stdout or ""

s = open(HTML, encoding="utf-8").read()
m = re.search(r'  var SCHOOL_DOM = (\{.*?\});', s, re.S)
DOM = json.loads(m.group(1))

# 详细项目的 (school, field, program)
pairs = []
for mm in re.finditer(r'\{s:"([^"]+)", p:"([^"]+)"[^\n]*?f:"([a-z]+)"', s):
    pairs.append((mm.group(1), mm.group(3), mm.group(2)))
seen, uniq = set(), []
for sp in pairs:
    k = (sp[0], sp[1])
    if k in seen: continue
    seen.add(k); uniq.append(sp)

KW = {
 "cs":["computer-science","computerscience","computer_science","mscs","ms-in-computer"],
 "ds":["data-science","datascience","analytics"],
 "ee":["electrical-engineering","electrical-and-computer"],
 "stat":["statistics","statistical"],
 "mis":["information-systems","information-management","information-science"],
 "fin":["finance"],
 "ai":["artificial-intelligence"],
 "ba":["business-analytics","analytics"],
 "me":["mechanical-engineering"],
 "ie":["industrial-engineering"],
 "che":["chemical-engineering"],
 "bme":["biomedical-engineering"],
 "civil":["civil-engineering"],
 "mse":["materials-science"],
 "aero":["aerospace-engineering"],
 "env":["environmental-engineering"],
 "biostat":["biostatistics"],
 "or":["operations-research"],
 "mba":["mba","business-administration"],
 "acct":["accounting"],
 "mkt":["marketing"],
 "mgmt":["management"],
 "econ":["economics"],
 "pp":["public-policy"],
 "pa":["public-administration"],
 "ph":["public-health"],
 "edu":["education"],
 "psy":["psychology"],
 "llm":["llm","laws"],
 "arch":["architecture"],
 "jour":["journalism"],
 "sw":["social-work"],
 "nrsg":["nursing"],
 "pharm":["pharmacy","pharmaceutical"],
 "ce":["computer-engineering"],
}

results = {}
schools = sorted({p[0] for p in uniq})
print("schools:", len(schools), "pairs:", len(uniq), flush=True)

for sch in schools:
    dom = DOM.get(sch)
    if not dom: continue
    sm = get("https://www." + dom + "/sitemap.xml", 12)
    if "<loc>" not in sm:
        sm = get("https://" + dom + "/sitemap.xml", 12)
    if "<loc>" not in sm:
        print("-- %-30s no sitemap" % sch, flush=True); continue
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    # 若是指向子 sitemap，跟随前 3 个
    if locs and all(u.endswith(".xml") for u in locs[:3]):
        sub = []
        for u in locs[:3]:
            x = get(u, 12); sub += re.findall(r"<loc>([^<]+)</loc>", x)
        locs = locs + sub
    for (sc, fid, prog) in [p for p in uniq if p[0]==sch]:
        kws = KW.get(fid, [])
        cands = [u for u in locs if any(k in u.lower() for k in kws)]
        cands = [u for u in cands if re.search(r"master|/ms-|graduate|masters", u.lower())] or cands
        cands.sort(key=lambda u: (len(u), u))
        if cands:
            results["%s|%s" % (sch, fid)] = cands[0]
            print("OK %-28s %-6s %s" % (sch[:28], fid, cands[0][:90]), flush=True)
        else:
            print("-- %-28s %-6s none" % (sch[:28], fid), flush=True)

json.dump(results, open("progurls.json","w"), ensure_ascii=False, indent=1)
print("FOUND", len(results), "/", len(uniq))
