---
title: 用 Astro 搭一个「不用维护」的技术博客
description: 从零到本地跑起来，理解内容集合、路由和构建产物，以及为什么静态站点对个人博客是正解。
date: 2026-10-08
tags: ['astro', 'tooling']
---

个人博客最大的敌人不是「不会搭」，是**搭完之后不想维护**。所以我选技术栈的标准只有一条：三个月不看它，它还得能跑。

静态站点生成器满足这个条件：产物是一堆 HTML，没有运行时，没有安全补丁，没有数据库迁移。

## 为什么是 Astro

同类选择里，Hugo 更快、Next.js 生态更大，我选 Astro 是因为它的默认行为符合博客的需求：

- **默认零 JavaScript**。页面就是 HTML，只有你显式写的交互才会有 JS
- **内容集合**（Content Collections）带类型校验，frontmatter 写错了构建直接失败
- **Markdown 开箱即用**，代码高亮内置，不用装一堆 remark 插件
- **岛屿架构**：以后想加评论区、搜索框，可以只给那一块加 JS

## 目录结构

一个博客真正需要的东西比想象中少：

```text
tech-blog/
├─ astro.config.mjs        # 站点配置：域名、集成、代码高亮
├─ src/
│  ├─ content.config.ts    # 内容集合：定义 frontmatter 的 schema
│  ├─ content/posts/       # ← 你只需要往这里放 .md
│  ├─ lib/                 # 工具函数：排序、标签、阅读时长
│  ├─ components/          # 页头、页脚、文章卡片
│  ├─ layouts/             # 页面骨架
│  ├─ pages/               # 路由：一个文件 = 一个 URL
│  └─ styles/global.css    # 全站样式
└─ public/                 # 原样拷贝的静态资源
```

`src/pages/` 是 Astro 的路由约定，文件名直接决定 URL：

| 文件 | 生成的地址 |
| --- | --- |
| `pages/index.astro` | `/` |
| `pages/about.astro` | `/about/` |
| `pages/blog/[...slug].astro` | `/blog/任意文章名/` |
| `pages/tags/[tag].astro` | `/tags/任意标签/` |

`[...slug]` 和 `[tag]` 是动态路由，需要导出 `getStaticPaths()` 告诉构建器要生成哪些页面。

## 内容集合与类型校验

这是 Astro 相比「手写 Markdown 解析」最大的优势。`src/content.config.ts` 里定义每篇文章必须具备什么字段：

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

于是每篇文章的开头长这样：

```md
---
title: 文章标题
description: 一句话摘要，会出现在列表页和搜索结果里
date: 2026-10-08
tags: ['astro', 'tooling']
draft: false
---
```

好处是**错误提前暴露**：日期写成 `2026-13-01`、标签写成字符串而不是数组，构建时就会失败，不会等到线上页面渲染出一片空白才发现。

## 渲染一篇文章的完整链路

`pages/blog/[...slug].astro` 里只有几行核心代码：

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

- `getStaticPaths()` 决定构建时要为哪些文章生成页面
- `render()` 同时返回渲染好的内容和**标题层级（headings）**

`headings` 这个返回值很关键——右侧的目录（TOC）就是用它生成的，不用再解析一遍 HTML。

```astro
{toc.length > 1 && (
  <aside class="post-aside">
    <Toc headings={headings} />
  </aside>
)}
```

## 构建与产物

```bash
pnpm install     # 安装依赖
pnpm dev         # 本地开发，默认 http://localhost:4321
pnpm build       # 生成静态站点到 dist/
pnpm preview     # 预览构建产物
```

`pnpm build` 之后，`dist/` 里是可以直接扔到任何静态托管的文件：

```text
dist/
├─ index.html
├─ blog/hello-blog/index.html
├─ tags/astro/index.html
├─ rss.xml
├─ sitemap-index.xml
└─ _astro/*.css
```

没有 Node 进程，没有容器，一台 CDN 就能扛。

## 这个博客已经有的东西

| 功能 | 实现方式 |
| --- | --- |
| 文章列表 / 详情 | 内容集合 + 动态路由 |
| 标签页、归档页 | 构建时聚合，无需前端查询 |
| RSS | `@astrojs/rss` |
| sitemap | `@astrojs/sitemap` |
| 深色模式 | CSS 变量 + `data-theme` |
| 代码高亮 | Shiki，双主题 |
| 阅读时长 | 按中文字符数估算 |

这些东西加起来不到 20 个文件，没有一行后端代码。

## 下一步

如果想继续加功能，推荐这个顺序：

1. **搜索**——`pagefind`，构建后扫一遍 HTML 建索引，零服务端
2. **评论**——`giscus`，挂在 GitHub Discussions 上，免费无广告
3. **统计**——Cloudflare Web Analytics 或 Umami，不收集个人数据

共同点是：**都不需要你维护服务器**。这条线最好别破。
