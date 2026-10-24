# 刊禾 · Biomed Reader 网站

公开网站：https://amiba-xqq.github.io/Biomedreader/

网站由 Jekyll 构建，包括主页、2.1 下载、底部 2.0 下载存档及 18 章使用教程；保留原网站配色与 2.0 共有操作截图。2.1 新功能按文字步骤说明。

## 文件与更新

- `index.html`、`downloads.html`、`guide.html`：页面正文及 YAML front matter。
- `_layouts/default.html`、`_includes/`：共享布局、导航、页脚和网盘按钮。
- `_data/downloads.json`：`version` 是当前 2.1；四个包记录文件名、GitHub/夸克链接、大小及 SHA256；`legacy` 独立保留原 2.0 的四组下载入口。更新时不要把旧版链接替换为新版。
- `site.js`：教程搜索、截图放大、手机菜单、复制校验值及公开 GitHub Releases 元数据检查。检查固定对应当前版本 tag，接口不可用时保留页面快照；历史 2.0 链接使用独立属性，不受脚本更新影响。
- `assets/`：软件图标与演示截图。
- `_config.yml`：站点地址和项目子路径。换域名或仓库时同步修改。

提交 `docs/` 的变更到 `main` 后，`.github/workflows/pages.yml` 自动运行 Jekyll、检查页面与下载映射，并发布 GitHub Pages。也可在 Actions 手动运行。Pages 发布源设为 GitHub Actions。

安装包保留在各平台 Releases 与夸克网盘，不提交到网站 Git 历史。当前 2.1 的夸克链接由维护者提供，旧版 2.0 保留原链接。SHA256 与大小来自对应 GitHub 安装包，未来替换同版本安装包时需要重新核对。教程明确区分 Windows COM 工具栏与 Mac 文档导出/CWYW 接管；Mac Word/EndNote 实机联动尚未验证。

## 本地预览（可选）

安装 Ruby 与 Jekyll 后，在本目录运行 `jekyll serve --baseurl /Biomedreader`，打开 `http://127.0.0.1:4000/Biomedreader/`。无需本地 Ruby 也可通过 GitHub Actions 构建与发布。
