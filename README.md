# 美国硕士选校推荐

一个**单文件、零依赖、零构建**的留学选校工具。双击 `index.html` 就能用，也可以直接丢到任意静态托管。

> 在线版：https://us-masters-planner.netlify.app

## 它能做什么

| 板块 | 功能 |
|---|---|
| 选校推荐 | 填背景（院校/GPA/TOEFL/GRE/预算/地区），自动分冲刺/匹配/保底，每张卡片带学费、生活费、城市、截止日、匹配度 |
| 反向选校 | 反过来：先定预算/地区/留不留美，再筛出符合条件的项目 |
| 我的清单 | 收藏、按截止日排序、倒计时、打印、CSV 导出、备份恢复 |
| 并排对比 | 选 2–3 个项目，13 个维度横向比 |
| 项目库 | 1117 个项目、105 所学校、35 个专业，可搜索、排序、按 GRE/学制/截止月筛选 |
| 费用地图 | 按城市看学费+生活费，支持"每年 / 整个学制"两种口径 |
| 时间线 | 通用倒排 + 基于你清单最早截止日的个性化倒排，可导出 .ics 日历 |
| 材料清单 | 美国硕士申请全流程 checklist，勾选状态本地保存 |
| 签证政策 | F-1 / OPT / STEM / CPT / H-1B |
| 数据来源 | 每个数字的来源、口径、抓取日期、更新记录 |

## 数据可信度（重要）

这个项目对数据的处理原则是：**能核实的标"已核实"，核不到的标"估算"，绝不把估算说成实测。**

| 数据 | 状态 |
|---|---|
| 生活费（39 个县） | ✅ MIT Living Wage 实测，逐县附原始链接 |
| 学费（4 条） | ✅ 官网核实（CMU / USC / UIUC / Cornell） |
| 学费（其余） | ⚠️ 按学校档位估算，显示为 `$95,000 ±9,000` |
| 项目页链接（6 条） | ✅ 直接指向招生页 |
| 项目页链接（其余） | ⚠️ 限定官网域名的搜索 |
| US News 综排 | ⚠️ 2026 版（2027 版此环境不可达），可点击修改 |
| 录取中位 GPA / 语言门槛 | ⚠️ 公开数据推算，非官方值 |

## 目录结构

```
.
├── index.html              # 全部代码（HTML + CSS + JS + 数据）
├── deploy/
│   ├── deploy-netlify.sh   # 一键部署脚本
│   ├── site.zip            # 可直接拖进 Netlify 的压缩包
│   └── README.md           # 部署说明
├── tools/
│   ├── schools.py          # 105 所学校表（排名/城市/类型/县 FIPS）
│   ├── gen_programs.py     # 生成批量项目条目
│   ├── fetch_livingwage.py # 抓 MIT Living Wage 各县生活成本
│   └── find_program_urls.py# 从 sitemap 找项目页线索（命中率低）
└── docs/
    └── 制作过程.md          # 完整的建设过程记录
```

## 本地使用

```bash
open index.html          # macOS
# 或
python3 -m http.server 8000   # 然后访问 http://localhost:8000
```

## 部署

**方式一：Netlify 拖拽**（最简单）
打开 https://app.netlify.com/drop ，把 `deploy/site.zip` 拖进去。

**方式二：命令行**
```bash
NETLIFY_TOKEN=nfp_xxx ./deploy/deploy-netlify.sh
```

**方式三：任意静态托管**
GitHub Pages / Cloudflare Pages / Vercel 都能直接托管 `index.html`，没有任何构建步骤。

## 数据更新流程

```bash
cd tools
python3 fetch_livingwage.py    # 更新生活费 → livingwage.json
python3 gen_programs.py        # 重新生成项目条目 → rows.json
```

然后把 `rows.json` 合并回 `index.html` 的 `PROGRAMS` 数组（具体见 `docs/制作过程.md` 第 5 节）。

## 已知局限

- 学费以估算为主，只有 4 条官网核实
- 项目页直达链接只有 6 条
- 排名是 2026 版
- "某校是否开设某专业"是按学校类型判断的，不是核实过的

## License

MIT
