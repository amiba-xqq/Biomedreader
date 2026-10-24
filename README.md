# 刊禾 · Biomed Reader 2.1

适用于 Windows 10/11 的生物医学文献检索与离线阅读软件。保存课题关键词，检索 PubMed、bioRxiv 与 medRxiv，管理收藏、笔记和本地 PDF。

## 网站与使用教程

[访问刊禾官网](https://amiba-xqq.github.io/Biomedreader/) · [下载（GitHub / 夸克网盘）](https://amiba-xqq.github.io/Biomedreader/downloads.html) · [详细使用教程](https://amiba-xqq.github.io/Biomedreader/guide.html)

网站使用 Jekyll 构建，由 GitHub Pages 公开托管，源码与维护说明见 [docs/README.md](docs/README.md)。

## 下载与安装

[打开 2.1 发布页](https://github.com/amiba-xqq/Biomedreader/releases/tag/v2.1)

| 下载文件 | 用途 |
| --- | --- |
| [BiomedReader_Setup_2.1_x64.exe](https://github.com/amiba-xqq/Biomedreader/releases/download/v2.1/BiomedReader_Setup_2.1_x64.exe) | Windows 10/11 64 位安装程序 |
| [BiomedReader_2.1_Portable_x64.zip](https://github.com/amiba-xqq/Biomedreader/releases/download/v2.1/BiomedReader_2.1_Portable_x64.zip) | Windows 10/11 64 位完整目录版，解压后运行 |
| [Release_Notes_2.1.txt](https://github.com/amiba-xqq/Biomedreader/releases/download/v2.1/Release_Notes_2.1.txt) | 最新更新说明 |
| [SHA256_Windows_2.1.txt](https://github.com/amiba-xqq/Biomedreader/releases/download/v2.1/SHA256_Windows_2.1.txt) | 下载文件的 SHA256 校验值 |

安装版运行安装程序；完整目录版需先解压全部文件，再运行文件夹中的 `BiomedReader.exe`，不要单独移动 EXE 或删除 `_internal`。升级前关闭 Biomed Reader 和 Word，原有本地数据保留。目录版需要 Word 插件时，关闭 Word 后运行 `RegisterWordAddin.cmd`；完整说明见压缩包内的 `Portable_README_2.1.txt`。

软件包含 Python 3.12、依赖库和内嵌浏览器，无需另外安装 Python。安装包未数字签名，Windows 可能显示发布者提示。

## 2.1 版本

应用、设置左下角、程序文件属性和安装程序使用产品版本 **2.1**，Windows 数字版本资源为 `2.1.0.0`，保留已有数据兼容性。

- 全部联网刷新依次处理关键词方案，并保留各来源增量检查点。
- 引用、Word 插件和 EndNote 导出保留 Volume、Issue、Pages。复制引用时卷页缺失则每次联网尝试补齐，完整则直接使用缓存。
- 批量收藏 PDF 支持多选/拖放、必选期刊目录和目标分组、识别首页完整标题、PubMed 匹配、自动关联 PDF、进度及失败名单。
- PDF 选择窗口独立显示，主窗口最小化后仍可拖入文件。
- Windows Word 插件保留插入/更新引用、Arial 五号默认字体和含嵌入文献库的 EndNote 文档导出。

本仓库发布 Windows 安装版和完整目录版。对应 macOS DMG 在 [独立仓库](https://github.com/amiba-xqq/Biomedreader_macos/releases/latest) 发布；Mac 2.1 使用 Word 文档导出及 EndNote CWYW 接管，不包含 Windows COM 工具栏。

## 快速开始

1. 在“关键词方案”点击“添加关键词组”，填写名称和检索表达式，例如 `R-loop OR "DNA-RNA hybrid"`。
2. 在“编辑方案”选择数据源、候选数、文章类型、年份和期刊目录。两个候选数默认 `0`，表示不限。
3. 点击“联网刷新”。预印本官网要求验证时，请手动完成验证，搜索窗口可以最小化。
4. 在表格或嵌入式卡片中阅读标题、期刊、JIF 和摘要，点击文章详情可打开 DOI、记录笔记。
5. 点击收藏后，在“收藏文章”的同名分组继续整理，也可建立自定义分组。
6. 收藏文章详情中链接自己下载的 PDF，随后通过“查看原文”使用默认 PDF 阅读器打开。

## 检索与阅读

- 每个关键词方案分别保存联网数据源，可选 PubMed、预印本或两者。在设置中选择预印本站点为 bioRxiv、medRxiv 或两者。
- 同时搜索两个预印本站点时，每个站点分别使用所设置的预印本候选数。
- PubMed 支持默认范围或标题与摘要。预印本支持默认、标题与摘要、全文或全文与标题摘要，最近年限默认两年。
- 文章类型可多选。期刊目录、最低 JIF 和文章类型筛选仅作用于 PubMed，多个期刊目录取并集。
- 首次完整建立缓存。条件不变时，后续按对应来源上次成功刷新日到本地今天进行增量搜索，合并并去重。
- 各来源独立记录成功检查点，单一来源失败不会让已完成来源重复完整检索。大缓存恢复时复用已有摘要，补取缺失记录。
- 检索分批保存新结果，取消后可查看本次已保存的新文章。需要核查全部历史范围时，勾选“完整检索”。
- 表格按需加载并支持调整列宽。卡片分页展示，可切换宽松或紧密密度，关键词卡片模式记录阅读位置。
- “检索源”只筛选已缓存来源。隐藏文章不会删除文章缓存和收藏，可以通过“隐藏设置”恢复显示。
- 支持最新发表、最相关与综合最佳排序。综合最佳使用 72% 相关性和 28% 时间新近度，时间权重约每 180 天减半。

官网和软件的结果可能因筛选条件、候选集、排序、收录延迟及检索完成状态而不同。按发表日期的严格增量可能遗漏晚收录的旧文，可通过完整检索核查。官网验证由用户手动完成，遇到限流请等待网站恢复。

## 收藏、PDF 和分享

收藏文章按实际收藏时的关键词方案名称归组，删除方案后收藏分组保留。可自定义分组、拖动排序，并复制或移动文章到其它组。

链接 PDF 时，软件将文件复制到当前数据目录的 `paper` 子文件夹，并以文章标题命名。最后一处收藏解除后会删除软件管理的 PDF 副本，保留原始下载文件与文章缓存。关键词方案中的“取消本组收藏”只移出本组，收藏文章详情的“取消收藏”解除该文全部分组归属。

收藏可以打包为 ZIP 分享。选择分组后，右侧仅显示这些组的文章，最终按文章勾选导出，可包含 PDF。接收者读取分享包后可获得分组、文章、笔记和 PDF 关联。

## 期刊目录与 JIF

内置 IF 6-10、IF 10-20、IF 20-500、NC精选与 NC扩选，可创建自定义目录、搜索部分名称或 ISSN、筛选 JIF 范围和只展示已选期刊。

IF 三组依据 2025 年 JIF 固定划分。显示 JIF 年份在设置中选择，默认本地年份减一，可选 2010 年至当前年。缺失值留空，切换展示年份不改变 IF 三组的成员。软件不在线补全 JIF，不调用 Clarivate Journals API。

期刊目录支持导出和读取分享 ZIP，同名导入目录追加 `_已重复`。NLM 公开目录收录不等同于 SCI 认证，JIF 以已录入年度数据为准。

## 数据位置与升级

默认位置为 `%LOCALAPPDATA%\OrangeReader\BiomedLiterature`，通常对应 `C:\Users\您的用户名\AppData\Local\OrangeReader\BiomedLiterature`。

升级前退出软件，并在设置中备份整个数据目录为 ZIP。已有方案、缓存、收藏、目录和 PDF 链接继续使用。卸载默认保留个人数据。

设置支持移动数据目录或链接已有数据目录。移动后使用新路径，验证完成后删除原数据。链接已有目录时，其中应直接包含 `biomed_literature.sqlite3`。浏览路径窗口支持输入或粘贴路径。

## 发布检查

此版本通过 32 项版本与关键功能回归检查，以及打包后的应用启动和内嵌浏览器离线自检。校验完整目录包的全部 ZIP CRC、关键运行库、内置期刊数据和编译代码与源码一致性。测试使用独立临时数据库。

依赖组件及其许可证信息见程序中的 `THIRD_PARTY_NOTICES.txt`。本仓库用于提供 Windows 发行文件与使用说明。


## 2026-10-19 更新（版本仍为 2.0）

- 设置增加“关键词方案默认展现形式”：宽松的嵌入式卡片、紧密的嵌入式卡片、表格。
- 默认使用紧密的嵌入式卡片。每次重启后，各方案恢复设置中的默认形式。
- 方案内临时切换展现形式与密度仅在本次运行有效，不修改全局默认值。
- 已访问 DOI 的文章保留原字体淡化颜色，背景保持白色。
- 32 项回归测试、打包应用及浏览器离线自检通过，缓存与 PDF 继续兼容。
