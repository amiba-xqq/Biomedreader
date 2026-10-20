# 刊禾 · Biomed Reader 网站

公开网站：https://amiba-xqq.github.io/Biomedreader/

网站由 Jekyll 构建，包括主页、下载与 14 章使用教程；保留原网站的配色和真实软件截图。所有截图中的文献为演示数据。

## 文件与更新

- `index.html`、`downloads.html`、`guide.html`：页面正文及 YAML front matter。
- `_layouts/default.html`、`_includes/`：共享布局、导航、页脚和网盘按钮。
- `_data/downloads.json`：四个 2.0 安装包的夸克链接，分别对应 Windows 安装版、Windows 完整目录版、Mac Apple Silicon 和 Mac Intel。更新网盘链接时应同步按钮上的版本说明。
- `site.js`：教程搜索、截图放大、手机菜单、复制校验值，以及公开 GitHub Releases 元数据检查。GitHub 接口不可用时使用页面中已验证的链接，不会改动夸克链接。
- `assets/`：软件图标与演示截图。
- `_config.yml`：站点地址和项目子路径。换域名或仓库时同步修改。

提交 `docs/` 的变更到 `main` 后，`.github/workflows/pages.yml` 自动运行 Jekyll、检查页面与下载映射，并发布 GitHub Pages。也可在 Actions 手动运行。Pages 发布源设为 GitHub Actions。

下载文件保留在各平台 Releases 与夸克网盘，不把安装包重复提交到 Git 历史。夸克文件目前固定为 2.0；将来升级时请自行上传对应文件，再更新链接及版本文案。教程及截图也应随版本核对。

## 本地预览（可选）

安装 Ruby 与 Jekyll 后，在本目录运行 `jekyll serve --baseurl /Biomedreader`，打开 `http://127.0.0.1:4000/Biomedreader/`。无需本地 Ruby 也可通过 GitHub Actions 构建与发布。
