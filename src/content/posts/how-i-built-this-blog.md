---
title: 我是怎么把这个博客搭起来的
description: 从选型到上线：为什么选 Astro、内容集合怎么工作、深色模式如何避免闪白，以及两个把我卡了一整天的部署坑。
date: 2026-10-19
tags: ['astro', 'tooling']
---

这个博客本身，大概是它将来所有文章里最值得复盘的一篇。下面按「定约束 → 选型 → 实现 → 上线 → 踩坑」的顺序写，代码都是能直接跑的版本。

## 先定约束，再选技术

我想写博客，但**不想维护网站**。所以所有决策都围绕一条：三个月不看它，它还得能跑。

具体约束：

- 文章用 Markdown 存在 Git 里，可迁移、可 diff、不会因为某个平台倒闭而丢
- 产出纯静态 HTML，没有数据库、没有服务端进程
- 发布就是 `git push`
- 托管最好免费

这四条一排，WordPress 那类就出局了——它要服务器、要定期打补丁、要备份数据库。我想要的是一堆文件，不是一个服务。

## 为什么是 Astro

比较了几个候选：

| 方案 | 优点 | 没选的原因 |
| --- | --- | --- |
| Hugo | 构建速度最快，单二进制 | 主题是 Go 模板，改设计成本高 |
| Next.js | 生态最大 | 博客用不上 SSR 和动态路由，配置面反而更大 |
| WordPress | 上手快、插件多 | 要服务器、要运维 |
| Astro | 默认零 JS、Markdown 原生、内容集合带类型 | — |

Astro 最打动我的是一句话：**默认不输出 JavaScript**。页面就是 HTML，只有当我自己写交互（主题切换、代码复制）时才会有 JS。对一个以文字为主的站点，这是最合适的默认值。

### 一个反直觉的决定：没用最新版

Astro 当时的最新版是 7.x，我用的是 **6.4.8**。

原因很实际：7.x 把底层换成了 Vite 8（rolldown 内核），我在 Windows 上构建时，它处理 CJS 依赖的 SSR 会直接崩溃，报 `require is not defined`。

退一个大版本，换 Vite 7 的成熟链路，构建一次就过。

> 能跑的稳定版，比最新版重要。博客是拿来写内容的，不是拿来追版本的。

## 目录结构

```text
D:\blog
├─ astro.config.mjs        站点配置：域名、sitemap、代码高亮
├─ pnpm-workspace.yaml     pnpm 设置（含依赖构建白名单）
├─ .github/workflows/
│  └─ deploy.yml           推送到 GitHub Pages
├─ public/                 原样拷贝的静态资源
├─ scripts/make-og.py      生成分享卡片图
├─ templates/post-template.md
└─ src/
   ├─ content.config.ts    内容集合的类型定义
   ├─ content/posts/       ← 文章都在这里
   ├─ lib/site.ts          站点信息
   ├─ lib/posts.ts         排序、标签、阅读时长
   ├─ components/          页头、页脚、卡片、目录、主题切换
   ├─ layouts/             页面骨架（含 SEO）
   ├─ pages/               路由：一个文件 = 一个 URL
   └─ styles/global.css    全站样式
```

路由是一张表就能说清的东西：

| 文件 | 地址 |
| --- | --- |
| `pages/index.astro` | `/` |
| `pages/about.astro` | `/about/` |
| `pages/blog/[...slug].astro` | `/blog/任意文章名/` |
| `pages/tags/[tag].astro` | `/tags/任意标签/` |

## 内容集合：让错误在构建时暴露

`src/content.config.ts` 用 zod 定义每篇文章必须长什么样：

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    description: z.string().default(''),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts };
```

于是文章开头必须是这样：

```md
---
title: 文章标题
description: 一句话摘要
date: 2026-10-19
tags: ['astro', 'tooling']
draft: false
---
```

好处是**错误提前暴露**：日期写成 `2026-13-01`、标签写成字符串而不是数组，构建时就会失败。而不是等到线上页面渲染出一片空白，你才回头找原因。

## 三个值得单独说的实现

### 一、文章的渲染链路

`src/pages/blog/[...slug].astro` 的核心只有几行：

```ts
export async function getStaticPaths() {
  const posts = await getPublishedPosts();
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content, headings } = await render(post);
```

`getStaticPaths()` 决定构建时要生成哪些页面。

`render()` 除了返回内容，还返回 **headings** —— 右侧那个悬浮目录就是用它生成的，不用再解析一遍 HTML。这个返回值省掉了一个常见的重复劳动。

### 二、深色模式：换变量，不换选择器

配色全部收在 CSS 变量里，`:root` 一套，`[data-theme='dark']` 一套：

```css
:root {
  --bg: #faf9f7;
  --ink: #1c1a17;
}

[data-theme='dark'] {
  --bg: #12100e;
  --ink: #ece8e1;
}
```

组件里只写 `color: var(--ink)`，于是切主题时没有任何一条规则需要重写，新加组件也不用考虑主题。

真正容易翻车的是**首屏闪白**：如果主题判断放在 `<body>` 末尾，页面会先按浅色渲染一帧再跳成深色。解决办法是把判断塞进 `<head>`，同步执行，早于任何绘制：

```html
<script is:inline>
  (function () {
    var theme = null;
    try {
      theme = localStorage.getItem('theme');
    } catch (e) {}
    if (theme !== 'light' && theme !== 'dark') {
      theme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.dataset.theme = theme;
  })();
</script>
```

`try/catch` 不是防御性编程的洁癖——Safari 隐私模式下访问 `localStorage` 会直接抛错，不包住整站就白屏。

### 三、代码高亮：一套内容，两套配色

普通文字换 CSS 变量就够了，但代码高亮是**构建时**由 Shiki 生成的行内颜色，它不认识 `data-theme`。

Astro 的做法是让 Shiki 同时输出两套颜色：

```js
// astro.config.mjs
markdown: {
  shikiConfig: {
    themes: { light: 'github-light', dark: 'github-dark' },
  },
},
```

生成的结构大致是：

```html
<span style="--shiki-light:#0550ae; --shiki-dark:#79c0ff">const</span>
```

然后只需要在深色模式下把变量接上：

```css
[data-theme='dark'] .astro-code,
[data-theme='dark'] .astro-code span {
  color: var(--shiki-dark) !important;
  background-color: var(--shiki-dark-bg) !important;
}
```

这里的 `!important` 是为了盖过 Shiki 写的行内 `color`。这是少数我认为它合理的地方：它在覆盖第三方生成的样式，而不是在给自己的代码打补丁。

## SEO 这些看不见的东西

一个博客没人访问，技术再好也没意义。所以基础项一次配齐：

- 每页独立的 `title` / `description` / `canonical`
- Open Graph 和 Twitter Card（分享到群里时有卡片）
- 文章页的 JSON-LD 结构化数据（`BlogPosting`）
- `@astrojs/rss` 生成 `/rss.xml`
- `@astrojs/sitemap` 生成 `sitemap-index.xml`
- `robots.txt` 用 endpoint 动态生成，里面的 Sitemap 地址跟着站点域名走

其中有个小设计：**站点地址从环境变量读，CI 里自动推导**，避免「忘了改 site 导致 RSS 里全是 example.com」这种静默错误。

```yaml
- name: Build
  run: pnpm build
  env:
    SITE_URL: https://${{ github.repository_owner }}.github.io
```

## 上线：GitHub Pages

仓库名必须是 `<用户名>.github.io`。这一点很关键：如果仓库叫 `blog`，站点会挂在 `https://用户名.github.io/blog/` 下面，而站内链接写的是 `/blog/xxx/` 这种根路径，会全部 404。

workflow 的关键部分：

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

三个权限缺一不可，尤其是 `id-token: write`，`deploy-pages` 靠它做 OIDC 认证。

然后用 `upload-pages-artifact` 打包 `dist/`，再 `deploy-pages` 发布。

## 卡住我的两个坑

这两件事加起来耗掉的时间，比写整个网站还多。

### 坑一：pnpm 11 把配置键名改了

CI 里 `pnpm install --frozen-lockfile` 直接退出 1：

```text
[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: esbuild@0.27.7, sharp@0.34.5
```

pnpm 10 起，出于供应链安全考虑，默认**不执行依赖的安装脚本**。要放行必须在 `pnpm-workspace.yaml` 里显式声明：

```yaml
allowBuilds:
  esbuild: true
  sharp: true
```

注意两点：

1. 网上大量教程还写着旧的 `onlyBuiltDependencies` 数组，在 pnpm 11 上**不生效**。
2. 这个错误在本机可能只是警告，到了 CI 会变成退出码 1，直接把 build 任务打挂。

### 坑二：PowerShell 把我自己的 workflow 写坏了

我用 PowerShell 脚本给 workflow 加环境变量，改完提交，结果 Actions 一直失败。

诡异的是：运行详情里 **job 数量是 0**。

0 个 job 这个特征非常关键——它说明 YAML 根本没被解析成功，流程还没进入构建阶段就死了。如果是某一步失败，你至少会看到 job 列表。

原因：`Get-Content -Raw` 在 Windows PowerShell 5.1 下默认按 ANSI（简体中文系统就是 GBK）解码，而文件是 UTF-8。读进来已经乱码，再写回去，两行中文注释被彻底毁掉，里面还混进了非法字符 `U+E047`。

改正的原则只有一句：**不要用会做隐式编码转换的命令读再写 UTF-8 文件**。

```powershell
# 正确：显式指定 UTF-8
$text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))
```

顺带说，那个 `$false` 是「不要 BOM」。带 BOM 的 YAML 在某些解析器里也会出问题。

### 附赠的教训：SSH 比 HTTPS 省心

一开始用 HTTPS 推代码，先是连不上（需要代理），接着是凭据管理器里存了个过期 token，每次推送都被 GitHub 判定无效。

换 SSH 之后就干净了：生成密钥、把公钥加到 GitHub、改远端地址，一次搞定，之后完全不用管认证。

## 结果

- 14 个页面，全部纯静态
- 零后端、零数据库、零追踪脚本
- 本地构建约 3 秒
- `git push` 之后约 1 分钟自动上线

维护成本基本为零。这大概是我做这个项目最满意的地方——它不会成为一个需要我照顾的东西。

## 接下来

- 站内搜索：Pagefind，构建后扫 HTML 建静态索引
- 评论：giscus，挂在 GitHub Discussions 上
- 可能换一个自定义域名，顺便解决国内访问不稳的问题

如果你也在犹豫要不要搭一个自己的博客，我的建议是：**先搭一个丑的，能发文章就行**。设计可以慢慢改，但「能发」这件事不解决，你就永远在挑主题。
