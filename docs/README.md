# 刊禾 · Biomed Reader 网站

GitHub Pages 官网：https://amiba-xqq.github.io/Biomedreader/

网站使用 Jekyll。首页展示科研工作流与学习路线；下载页包含 2.2.2 四款安装包及历史版本；学习中心包含 34 章和版本导览。原有教程的锚点保留。

- `index.html`、`downloads.html`、`guide.html`：页面正文。
- `_layouts/`、`_includes/`：共享布局、图标、下载卡片及新增科研课程。
- `_data/downloads.json`：四个当前包的文件名、GitHub / 夸克链接、大小和 SHA‑256。`previous` 对应 2.1，`legacy` 对应 2.0。
- `app-update.json`：桌面软件读取的更新清单，使用同一组数据。完整目录 ZIP 通过下载页提供。
- `site.js`：教程筛选、目录高亮、截图放大、减少动态效果支持和复制校验值。安装包链接已写入页面，无需调用 GitHub API 才能使用。
- `assets/`：软件图标及 2.2.2 演示截图（`assets/guide-222/`）。截图尺寸、替代文本和说明在 `_data/guide_shots.json` 维护。

维护者替换同版本安装包时，请从 GitHub Release 核对文件名、字节数和校验值，同步 `_data/downloads.json` 与 CI 校验。用户提供的夸克入口与 GitHub 文件分别核对，历史版本链接保留。

提交 `docs/` 变更至 `main` 后，GitHub Actions 构建 Jekyll、检查页面和校验清单并部署。可在本目录通过 `jekyll serve --baseurl /Biomedreader` 本地预览。
