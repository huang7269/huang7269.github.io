---
title: 深色模式的三种做法，以及我为什么选 CSS 变量
description: 从 prefers-color-scheme 到 class 切换再到 data 属性，比较三种实现方式的代价，包括那个所有人都踩过的闪白问题。
date: 2026-09-28
tags: ['css', 'design']
---

深色模式看起来是个小需求，但真做起来有三个坑：**闪白、状态同步、以及代码高亮的两套配色**。这篇文章按复杂度递增讲三种做法。

## 方案一：只跟系统走

最省事的做法，一行 CSS 都不用写 JS：

```css
:root {
  --bg: #faf9f7;
  --ink: #1c1a17;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #12100e;
    --ink: #ece8e1;
  }
}

body {
  background: var(--bg);
  color: var(--ink);
}
```

优点：没有 JavaScript，没有闪烁，系统改了自动跟随。

缺点：**用户无法覆盖**。有人系统是深色，但看文档时想用浅色，做不到。

## 方案二：给 html 加 class

想给用户选择权，就得把状态存下来：

```js
const root = document.documentElement;
const saved = localStorage.getItem('theme');

if (saved === 'dark' || (!saved && matchMedia('(prefers-color-scheme: dark)').matches)) {
  root.classList.add('dark');
}
```

CSS 用 `.dark` 作为前缀：

```css
.dark body {
  background: #12100e;
  color: #ece8e1;
}
```

这能工作，但问题是**选择器优先级**。`.dark body` 比 `body` 高一级，于是你后面所有针对 `body` 的样式都得跟着加 `.dark` 前缀，很快就失控。

## 方案三：data 属性 + CSS 变量（推荐）

把「主题名」当成一个数据，而不是一组样式覆盖：

```html
<html data-theme="dark">
```

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

区别在于：**只换变量，不换选择器**。所有组件都写 `color: var(--ink)`，于是切主题时没有任何一条规则需要重写。新加组件也不用考虑主题。

切换逻辑也只有三行：

```js
btn.addEventListener('click', () => {
  const root = document.documentElement;
  const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
  root.dataset.theme = next;
  localStorage.setItem('theme', next);
});
```

## 那个所有人都踩的坑：闪白

如果主题判断写在 `<script>` 里，而脚本在 `<body>` 末尾，那么页面会先按浅色渲染一帧，再跳成深色。深色模式用户每次刷新都被闪一下，体验极差。

解决方式是**把判断塞进 `<head>`，同步执行，早于任何绘制**：

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

几个细节值得注意：

- 用 `is:inline`（Astro 里）让脚本内联，不被打包成异步加载的外部文件
- `try/catch` 包住 `localStorage`，Safari 隐私模式下访问会直接抛错
- 脚本必须放在 `<head>` 里，且不能加 `defer` / `async`
- 顺便设置 `<meta name="theme-color">`，让手机浏览器地址栏也跟着变

> 判断主题的脚本每多一次网络往返，闪白就多一帧。这个位置不能省。

## 代码高亮的双主题

这是最容易被忽略的部分。普通文本换 CSS 变量就够了，但代码高亮是**构建时**由 Shiki 生成的内联颜色：

```html
<span style="color:#0550ae">const</span>
```

它不认识你的 `data-theme`。Astro 的做法是让 Shiki 同时输出两套颜色，存进 CSS 变量：

```js
// astro.config.mjs
markdown: {
  shikiConfig: {
    themes: { light: 'github-light', dark: 'github-dark' },
  },
}
```

生成的结构大致是：

```html
<span style="--shiki-light:#0550ae; --shiki-dark:#79c0ff">const</span>
```

你只需要在深色模式下把变量接上去：

```css
[data-theme='dark'] .astro-code,
[data-theme='dark'] .astro-code span {
  color: var(--shiki-dark) !important;
  background-color: var(--shiki-dark-bg) !important;
}
```

`!important` 在这里是必要的——要盖过 Shiki 写的行内 `color`。这是少数我认为 `!important` 合理的地方：**它在覆盖第三方生成的内联样式，而不是在打补丁自己的代码**。

## 小结

| 方案 | 用户可切换 | 优先级失控风险 | 闪白 |
| --- | --- | --- | --- |
| 媒体查询 | 否 | 无 | 无 |
| class 覆盖 | 是 | 高 | 需额外处理 |
| data + 变量 | 是 | 无 | 需额外处理 |

选择第三种，把「主题」当成状态而不是样式，后面加多少组件都不会返工。
