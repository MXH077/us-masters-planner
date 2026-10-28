#!/bin/bash
# 用法: NETLIFY_TOKEN=nfp_xxx ./deploy-netlify.sh
set -e
TOKEN="${NETLIFY_TOKEN:?需要 NETLIFY_TOKEN}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ZIP="$HERE/site.zip"

echo "1/3 创建站点..."
SITE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"us-masters-'$RANDOM'"}' \
  https://api.netlify.com/api/v1/sites)

SITE_ID=$(printf '%s' "$SITE" | python3 -c "import sys,json;print(json.load(sys.stdin).get('id',''))")
SITE_URL=$(printf '%s' "$SITE" | python3 -c "import sys,json;print(json.load(sys.stdin).get('ssl_url',''))")
if [ -z "$SITE_ID" ]; then echo "创建失败: $SITE"; exit 1; fi
echo "    站点: $SITE_URL"

echo "2/3 上传 site.zip ..."
DEPLOY=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/zip" \
  --data-binary "@$ZIP" \
  https://api.netlify.com/api/v1/sites/$SITE_ID/deploys)

STATE=$(printf '%s' "$DEPLOY" | python3 -c "import sys,json;print(json.load(sys.stdin).get('state',''))")
echo "    状态: $STATE"

echo "3/3 完成: $SITE_URL"
