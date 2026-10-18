// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// ⚠️ 上线前把 site 改成你自己的域名，RSS / sitemap / 分享卡片都依赖它
export default defineConfig({
  site: 'https://blog.example.com',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      // 双主题：浅色用 github-light，深色用 github-dark
      themes: { light: 'github-light', dark: 'github-dark' },
      wrap: false,
    },
  },
});
