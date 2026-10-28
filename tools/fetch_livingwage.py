# 抓取 MIT Living Wage Calculator 各县年度生活成本（分项）
# 输出 livingwage.json：{县名: {fips, page_title, url, parts, total}}
import re, html, subprocess, json, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

COUNTIES = {
 "Middlesex, MA (Cambridge/Boston)": "25017",
 "Santa Clara, CA (Palo Alto)": "06085",
 "Allegheny, PA (Pittsburgh)": "42003",
 "Alameda, CA (Berkeley)": "06001",
 "Champaign, IL (Urbana)": "17019",
 "Fulton, GA (Atlanta)": "13121",
 "Los Angeles, CA": "06037",
 "New York, NY": "36061",
 "Orange, CA (Irvine)": "06059",
 "Suffolk, MA (Boston)": "25025",
 "Cook, IL (Chicago)": "17031",
 "Durham, NC": "37063",
 "Travis, TX (Austin)": "48453",
 "San Diego, CA": "06073",
 "Monroe, NY (Rochester)": "36055",
 "Bronx, NY (Fordham)": "36005",
 "Onondaga, NY (Syracuse)": "36067",
 "Maricopa, AZ (Tempe)": "04013",
 "Washtenaw, MI (Ann Arbor)": "26161",
 "Middlesex, NJ (New Brunswick)": "34023",
 "Dane, WI (Madison)": "55025",
 "Tippecanoe, IN (West Lafayette)": "18157",
 "Brazos, TX (College Station)": "48041",
 "Wake, NC (Raleigh)": "37183",
 "Essex, NJ (Newark)": "34013",
 "Fairfax, VA": "51600",
 "Erie, NY (Buffalo)": "36029",
 "Hamilton, OH (Cincinnati)": "39061",
 "St. Louis, MO": "29189",
 "King, WA (Seattle)": "53033",
 "Mercer, NJ (Princeton)": "34021"
}

def fetch(fips):
    url = "https://livingwage.mit.edu/counties/" + fips
    r = subprocess.run(["curl","-sL","-m","25","-A",UA,url], capture_output=True, text=True)
    return url, r.stdout or ""

def parse(h):
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S|re.I)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' | ', h)))
    t = re.sub(r'(\s*\|\s*)+', ' | ', t)
    title = re.search(r'Living Wage Calculation for ([^|]{3,60})', t)
    # 1 adult 列：Food $7,116 | Child Care $0 | Medical ... | Housing ... | Transportation ... | Civic ... | Internet ...
    vals = {}
    for key in ["Food","Housing","Transportation","Civic","Internet & Mobile","Medical"]:
        m = re.search(re.escape(key) + r'\s*\|\s*\$([\d,]+)', t)
        if m: vals[key] = int(m.group(1).replace(',',''))
    return (title.group(1).strip() if title else "?"), vals

out = {}
for name, fips in COUNTIES.items():
    url, h = fetch(fips)
    open('lw_%s.html' % fips, 'w').write(h)
    title, vals = parse(h)
    total = sum(vals.values()) if vals else 0
    out[name] = {"fips": fips, "page_title": title, "url": url, "parts": vals, "total": total}
    print("%-38s %-6s %-7s %s" % (name, fips, total or "ERR", title[:40]))

json.dump(out, open("livingwage.json","w"), ensure_ascii=False, indent=1)
print("saved", len(out))
