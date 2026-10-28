# 部署

## 一键部署到 Netlify

```bash
NETLIFY_TOKEN=nfp_xxx ./deploy-netlify.sh
```

脚本会：创建站点 → 上传 site.zip → 返回正式地址。

## 手动部署

打开 https://app.netlify.com/drop ，把 `site.zip` 拖进去即可，无需命令行。

## 更新已有站点

```bash
cd .. && zip -q -r deploy/site.zip index.html
NETLIFY_TOKEN=nfp_xxx ./deploy/deploy-netlify.sh
```

或在 Netlify 后台的 Deploys 页面直接拖入新的 zip。

## 其他托管

`index.html` 是纯静态文件，GitHub Pages / Cloudflare Pages / Vercel 都能直接托管，无需构建。
