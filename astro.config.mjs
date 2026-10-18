// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 站点地址：RSS、sitemap、canonical、分享卡片都依赖它。
// 可以用环境变量 SITE_URL 覆盖；GitHub Actions 里已自动设为
// https://<仓库所有者>.github.io，所以部署时不用手改这里。
// 本地想验证真实地址：$env:SITE_URL="https://你的名字.github.io"; pnpm build
export default defineConfig({
  site: process.env.SITE_URL || 'https://blog.example.com',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      // 双主题：浅色用 github-light，深色用 github-dark
      themes: { light: 'github-light', dark: 'github-dark' },
      wrap: false,
    },
  },
});