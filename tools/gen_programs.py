# 生成 100 所学校的批量项目条目（学费按档位区间估算）
# 输出 rows.json，再由 merge 步骤写回 index.html 的 PROGRAMS 数组
import sys, json, random, os
sys.path.insert(0, os.path.dirname(__file__))
from schools import SCHOOLS

LW = json.load(open('livingwage.json'))
COUNTY = {v['fips']: v for v in LW.values()}
def living(fips, city):
    if fips and fips in COUNTY:
        p = COUNTY[fips]['parts']
        return round(p.get('Housing',0)*0.6 + p.get('Food',0) + p.get('Transportation',0) + p.get('Internet & Mobile',0))
    return None

# id, 中文名, 学位名, pre, ddl, dur, diff调, 学费系数
FIELDS = [
 ("cs","计算机科学","MS in Computer Science","hard","12/15",2,0.04,1.05),
 ("ai","人工智能","MS in Artificial Intelligence","hard","12/15",2,0.02,1.05),
 ("ds","数据科学","MS in Data Science","soft","12/15",1.5,0.02,1.05),
 ("ba","商业分析","MS in Business Analytics","soft","01/15",1,0.02,1.15),
 ("ee","电子工程","MS in Electrical Engineering","hard","12/15",2,0.0,1.0),
 ("ce","计算机工程","MS in Computer Engineering","hard","12/15",2,0.0,1.0),
 ("me","机械工程","MS in Mechanical Engineering","hard","01/15",2,-0.02,0.95),
 ("ie","工业工程","MS in Industrial Engineering","hard","01/15",1.5,-0.02,0.95),
 ("che","化学工程","MS in Chemical Engineering","hard","01/15",2,-0.02,0.95),
 ("bme","生物医学工程","MS in Biomedical Engineering","hard","01/15",2,0.0,1.0),
 ("civil","土木工程","MS in Civil Engineering","hard","01/15",2,-0.05,0.9),
 ("mse","材料科学","MS in Materials Science","hard","01/15",2,-0.03,0.95),
 ("aero","航空航天","MS in Aerospace Engineering","hard","01/15",2,-0.03,0.95),
 ("env","环境工程","MS in Environmental Engineering","hard","01/15",2,-0.06,0.9),
 ("stat","统计学","MS in Statistics","soft","01/15",1.5,0.02,1.0),
 ("biostat","生物统计","MS in Biostatistics","soft","01/15",2,0.0,1.0),
 ("or","运筹学","MS in Operations Research","hard","01/15",1.5,0.0,1.0),
 ("mis","信息系统","MS in Information Systems","soft","01/15",1.5,0.0,1.0),
 ("mba","工商管理硕士","Master of Business Administration (MBA)","none","01/05",2,0.05,1.3),
 ("fin","金融","MS in Finance","none","01/15",1,0.03,1.25),
 ("acct","会计","MS in Accounting","none","01/15",1,0.0,1.15),
 ("mkt","市场营销","MS in Marketing","none","01/15",1,0.0,1.15),
 ("mgmt","管理学","MS in Management","none","01/15",1,-0.02,1.1),
 ("econ","经济学","MS in Economics","soft","12/15",2,0.03,1.0),
 ("pp","公共政策","Master of Public Policy","none","01/15",2,0.0,0.95),
 ("pa","公共管理","Master of Public Administration","none","01/15",2,-0.02,0.9),
 ("ph","公共卫生","Master of Public Health","soft","01/15",2,0.0,0.95),
 ("edu","教育学","MS in Education","none","01/15",1.5,-0.10,0.7),
 ("psy","心理学","MS in Psychology","soft","12/01",2,0.02,0.9),
 ("llm","法学 LLM","Master of Laws (LLM)","none","02/15",1,0.02,1.2),
 ("arch","建筑学","Master of Architecture","soft","01/15",2,0.0,1.0),
 ("jour","新闻传播","MS in Journalism","none","01/15",1.5,-0.05,1.0),
 ("sw","社会工作","Master of Social Work","none","01/15",2,-0.12,0.75),
 ("nrsg","护理学","MS in Nursing","soft","01/15",2,-0.08,0.8),
 ("pharm","药学","MS in Pharmaceutical Sciences","hard","01/15",2,-0.05,1.1),
]
F = {f[0]: f for f in FIELDS}

ARCH = {
 "tech":  ["cs","ee","me","ds","ai","ce","ie","che","bme","mse","aero","or","stat","econ","mba"],
 "big":   ["cs","ds","mba","ee","stat","fin","econ","bme","psy","ph","pp","mis","acct","edu","llm","arch","jour","biostat","mkt","mgmt","sw","nrsg","pa","ai","ba"],
 "public":["cs","ds","mba","ee","me","stat","fin","econ","bme","ie","civil","env","ph","edu","psy","mis","acct","pp","pa","llm","arch","jour","sw","nrsg","che","mse","aero","ai","ba","biostat","or","mkt","mgmt","pharm"],
 "city":  ["cs","ds","mba","fin","mis","ba","acct","mkt","mgmt","econ","pp","pa","jour","sw","ai"],
}
N = {"tech":9,"big":9,"public":9,"city":7}

def base_tuit(school):
    rank, typ = school[3], school[4]
    if typ == "private":
        if rank <= 10: return (66000, 80000)
        if rank <= 25: return (58000, 72000)
        if rank <= 50: return (52000, 66000)
        return (45000, 60000)
    else:
        if rank <= 10: return (32000, 50000)
        if rank <= 25: return (28000, 45000)
        if rank <= 50: return (26000, 42000)
        return (22000, 38000)

def base_d(rank): 
    if rank <= 10: return 0.88
    if rank <= 20: return 0.82
    if rank <= 35: return 0.75
    if rank <= 50: return 0.66
    if rank <= 65: return 0.58
    if rank <= 80: return 0.50
    return 0.42

def base_gpa(rank):
    if rank <= 10: return 3.70
    if rank <= 25: return 3.60
    if rank <= 50: return 3.50
    return 3.40

# 两轮生成：先保证核心方向覆盖，再按上限摊开其他方向
CORE = ["cs","ds","mba","ee"]
FIELD_CAP = 22
counts = {}
plan = []

def fields_for(arch):
    return ARCH[arch]

# 第一轮：核心方向（每校 4 个）
for sch in SCHOOLS:
    name, city, st, rank, typ, arch, fips = sch
    fs = [f for f in CORE if f in ARCH[arch]]
    if not fs: fs = ARCH[arch][:2]
    plan.append((sch, fs))
    for f in fs: counts[f] = counts.get(f, 0) + 1

# 第二轮：其余方向，按上限补齐
for sch in SCHOOLS:
    name, city, st, rank, typ, arch, fips = sch
    extra = []
    for f in ARCH[arch]:
        if f in CORE: continue
        if counts.get(f, 0) < FIELD_CAP:
            extra.append(f); counts[f] = counts.get(f, 0) + 1
    if extra: plan.append((sch, extra))

ROWS = []
for (school, field_ids) in plan:
    (name, city, st, rank, typ, arch, fips) = school
    for fid in field_ids:
        lv = living(fips, city)
        liv = lv if lv else 28000
        lo, hi = base_tuit((name,city,st,rank,typ))
        f = F[fid]
        t_lo = round(lo * f[7] / 1000) * 1000
        t_hi = round(hi * f[7] / 1000) * 1000
        tuit = round((t_lo + t_hi) / 2)
        d = max(0.12, min(0.95, base_d(rank) + f[6]))
        gpa = round(max(3.0, base_gpa(rank) - (0.05 if f[3]=="none" else 0)), 2)
        toefl = 100 if f[3]=="hard" else (90 if f[3]=="soft" else 85)
        gre = "req" if fid in ("mba",) else "opt"
        ROWS.append({
            "s": name, "p": f[2], "city": city, "st": st,
            "reg": ("west" if st in ("CA","WA","OR","AZ","CO","UT","NV") else
                    "northeast" if st in ("MA","NY","NJ","PA","CT","RI","NH","VT","ME","MD","DC","DE") else
                    "south" if st in ("TX","FL","GA","NC","SC","VA","TN","AL","MS","LA","KY","WV","OK","AR") else "midwest"),
            "ct": "大城市" if city in ("New York","Los Angeles","Chicago","Boston","Philadelphia","San Francisco","Seattle","Washington","Atlanta","Houston","Dallas","Miami") else "中型城市",
            "tuit": tuit, "tlo": t_lo, "thi": t_hi, "liv": liv, "dur": f[5], "d": round(d, 2),
            "gpa": gpa, "toefl": toefl, "gre": gre, "ddl": f[4], "f": fid,
            "pre": f[3], "rk": rank, "est": 1,
            "note": ("学费为该校档位区间估算" if lv else "学费与生活费均为估算"),
        })
print("rows", len(ROWS))
json.dump(ROWS, open('rows.json','w'), ensure_ascii=False, separators=(',',':'))
from collections import Counter
print(Counter(r['f'] for r in ROWS).most_common(8))
print(Counter(r['s'] for r in ROWS).most_common(3))
