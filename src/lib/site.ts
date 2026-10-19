/**
 * 站点信息 —— 改这里就能改全站标题、描述、作者、社交链接。
 * 注意：域名还要同步改 astro.config.mjs 里的 `site`。
 */
export const SITE = {
  title: '灰度',
  tagline: '工程实践 · 系统设计 · 踩坑复盘',
  description:
    '一个程序员的技术笔记本。记录工程实践、系统设计、以及那些踩过坑才想明白的事。',
  author: '灰度',
  url: 'https://huang7269.github.io',
  github: 'https://github.com/huang7269',
  email: 'huang7269@outlook.com',
  locale: 'zh-CN',
} as const;
