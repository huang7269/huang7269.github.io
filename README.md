# 灰度 · 个人技术博客

一个用 [Astro](https://astro.build) 构建的纯静态技术博客：Markdown 写作、零 JavaScript 运行时、无后端、无数据库。

## 快速开始

```bash
# 需要 Node.js 20+
node -v

pnpm install     # 安装依赖（也可以用 npm install）
pnpm dev         # 本地开发 → http://localhost:4321
```

改完内容后：

```bash
pnpm build       # 生成静态站点到 dist/
pnpm preview     # 本地预览 dist/ 的构建产物
```

## 目录结构

```text
.
├─ astro.config.mjs        # 站点配置：域名、sitemap、代码高亮主题
├─ src/
│  ├─ content.config.ts    # 内容集合：frontmatter 的类型定义（zod schema）
│  ├─ content/posts/       # ★ 文章目录，你只需要往这里放 .md
│  ├─ lib/site.ts          # ★ 站点标题、描述、作者、社交链接
│  ├─ lib/posts.ts         # 排序、标签统计、阅读时长等工具函数
│  ├─ components/          # 页头、页脚、文章卡片、目录、主题切换
│  ├─ layouts/             # 页面骨架（含 SEO / OG / JSON-LD）
│  ├─ pages/               # 路由：一个文件 = 一个 URL
│  └─ styles/global.css    # 全站样式（含深色模式变量）
├─ public/                 # 原样拷贝的静态资源（favicon、og 图）
└─ scripts/make-og.py      # 生成分享卡片图（可选）
```

## 写一篇新文章

1. 在 `src/content/posts/` 新建 `你的标题.md`
2. 开头写 frontmatter（可复制 `templates/post-template.md`）：

```md
---
title: 文章标题
description: 一句话摘要，会出现在列表页、RSS 和搜索结果里
date: 2026-10-18
tags: ['astro', 'tooling']
draft: false
---

正文从这里开始。
```

字段说明：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | 是 | 文章标题 |
| `date` | 是 | 发布日期，`YYYY-MM-DD` |
| `description` | 否 | 摘要，列表页和分享卡片用 |
| `tags` | 否 | 标签数组，建议用英文/拼音，直接进 URL |
| `draft` | 否 | `true` 时不会出现在任何页面和 RSS 里 |
| `updated` | 否 | 更新日期 |

文件名就是 URL：`hello-world.md` → `/blog/hello-world/`。

## 改成你自己的

| 要改什么 | 改哪里 |
| --- | --- |
| 站点名、描述、作者、GitHub、邮箱 | `src/lib/site.ts` |
| 域名（影响 RSS、sitemap、分享卡片） | `astro.config.mjs` 里的 `site` |
| 配色、字体、间距 | `src/styles/global.css` 顶部的 CSS 变量 |
| 导航菜单 | `src/components/Header.astro` 的 `nav` 数组 |
| 关于页正文 | `src/pages/about.astro` |
| 分享卡片图 | 改 `scripts/make-og.py` 里的文字后 `python scripts/make-og.py` |

## 已经有的东西

- 文章列表 / 详情 / 标签页 / 归档页
- 标签聚合、按年份归档
- 深色模式（跟随系统 + 手动切换 + 记忆选择，无闪白）
- 代码高亮（Shiki 双主题）+ 一键复制
- 文章目录（TOC，宽屏右侧悬浮）
- RSS、sitemap、robots.txt
- 每页 SEO meta、Open Graph、JSON-LD 结构化数据
- 移动端适配

## 部署

站点是纯静态的，`dist/` 扔到任何静态托管都能跑。仓库里已经带好 GitHub Pages 的自动部署配置
（`.github/workflows/deploy.yml`），push 到 `main` 就会自动构建并发布。

### GitHub Pages（已配置）

1. 新建仓库，**名字用 `<你的用户名>.github.io`**（例如 `alice.github.io`）。
   这样站点在根路径 `https://alice.github.io/`，现有链接不用改。
2. 推代码：

   ```bash
   git init
   git add -A
   git commit -m "init blog"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/<你的用户名>.github.io.git
   git push -u origin main
   ```

3. 把 `astro.config.mjs` 里的 `site` 改成 `https://<你的用户名>.github.io`
4. 仓库 → Settings → Pages → Build and deployment → Source 选 **GitHub Actions**
5. 等 Actions 跑完（约一分钟），访问 `https://<你的用户名>.github.io`

> 仓库如果不叫 `<用户名>.github.io`（比如叫 `blog`），站点会挂在 `https://用户名.github.io/blog/` 下。
> 那样需要给 `astro.config.mjs` 加 `base: '/blog'`，并且把站内所有绝对链接改成带 base 的形式——
> 当前代码还没做这层适配。

### 其他平台

- **Cloudflare Pages**：Connect to Git → Framework preset `Astro`，Build `pnpm build`，Output `dist`
- **Vercel**：导入仓库，自动识别 Astro
- **Netlify**：同上

如果主要读者在国内且要求稳定，再考虑国内云 + 域名备案。

## 几个容易踩的坑

**中文标点紧贴 `**` 会解析失败**

CommonMark 要求闭合的 `**` 后面不能紧跟文字字母。所以：

```md
✅ **内容集合**（Content Collections）带类型校验
❌ **内容集合（Content Collections）**带类型校验   ← 不会加粗
```

规则是：`**` 闭合时，要么后面是空格/标点/换行，要么前面不是标点。中文括号 `）`、`」` 都算标点。

**Windows 上 pnpm 报 junction 相关错误**

本项目带了 `pnpm-workspace.yaml` 并设置 `nodeLinker: hoisted`，让 `node_modules` 是扁平的真实目录，避免 Windows 权限或路径解析问题。如果仍异常，执行 `pnpm config set node-linker hoisted` 后重新 `pnpm install`。

**端口被占用**

`pnpm dev --port 4322` 换一个端口。

## 下一步可以加

按「不需要维护服务器」的原则，推荐顺序：

1. **站内搜索** — [Pagefind](https://pagefind.app/)，构建后扫 HTML 建索引，纯静态
2. **评论** — [giscus](https://giscus.app/)，挂在 GitHub Discussions 上，免费无广告
3. **访问统计** — Cloudflare Web Analytics 或 [Umami](https://umami.is/)，不收集个人数据
