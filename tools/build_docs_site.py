#!/usr/bin/env python
"""构建 fastfeishu 文档站点（GitHub Pages）。

用法：
    python tools/build_docs_site.py            # 输出到 ./site
    python tools/build_docs_site.py --out dist # 指定输出目录

产物为纯静态 HTML（左侧导航 + 右侧正文），无需 Node / 主题框架，
直接把 site/ 目录配置为 GitHub Pages 的发布来源即可。
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import os
from pathlib import Path

from markdown_it import MarkdownIt
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments import highlight
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ASSETS = ROOT / "assets"

SITE_TITLE = "fastfeishu 文档"
SITE_TAGLINE = "飞书 Sheets API v3 的 Python 高级封装"
REPO_URL = "https://github.com/jibuzixin/fastfeishu"

# (分组标题, [(页面标题, markdown 源路径)]) —— 源路径相对仓库根目录
NAV = [
    ("开始", [
        ("项目首页", "README.md"),
        ("快速上手", "docs/getting-started.md"),
        ("项目架构", "docs/ARCHITECTURE.md"),
    ]),
    ("使用指南", [
        ("基础操作", "docs/basic-operations.md"),
        ("单元格类型", "docs/cell-types.md"),
        ("批量处理工具", "docs/batch-utils.md"),
        ("Sheet 管理", "docs/sheet-management.md"),
        ("API 参考与异常", "docs/api-reference.md"),
        ("文档导出", "docs/EXPORT_GUIDE.md"),
    ]),
    ("参与开发", [
        ("贡献指南", "docs/CONTRIBUTING.md"),
        ("测试指南", "docs/TESTING.md"),
        ("集成测试指南", "docs/INTEGRATION_TESTS.md"),
    ]),
]

PAGES = [(title, src) for _, items in NAV for title, src in items]


# --------------------------------------------------------------------------- #
# Markdown 渲染
# --------------------------------------------------------------------------- #
LIGHT_STYLE = HtmlFormatter(nowrap=True, cssclass="hljs").get_style_defs(".hljs")
DARK_STYLE = HtmlFormatter(nowrap=True, style="monokai").get_style_defs(".hljs")


def highlight_css() -> str:
    """亮色用默认配色，暗色模式切换为 monokai，保证代码块对比度。"""
    return (
        LIGHT_STYLE
        + "\n@media (prefers-color-scheme: dark) {\n"
        + "\n".join("  " + line for line in DARK_STYLE.strip().splitlines())
        + "\n}\n"
    )


def build_highlighter() -> tuple[HtmlFormatter, MarkdownIt]:
    formatter = HtmlFormatter(nowrap=True, cssclass="hljs")
    md = (
        MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": False})
        .enable("table")
        .enable("strikethrough")
    )

    def fence(self, tokens, idx, options, env=None):  # noqa: ARG001
        """用 Pygments 高亮代码块，失败时回退为纯文本 <pre>。"""
        token = tokens[idx]
        info = (token.info or "").strip().split()
        lang = info[0] if info else ""
        code = token.content
        lexer = None
        for candidate in (lang, ""):
            try:
                lexer = get_lexer_by_name(candidate) if candidate else guess_lexer(code)
                break
            except ClassNotFound:
                continue
        if lexer is None:
            return False
        return f'<pre><code class="hljs">{highlight(code, lexer, formatter)}</code></pre>\n'

    md.add_render_rule("fence", fence)
    return formatter, md


def rewrite_links(md_text: str, source: Path) -> str:
    """把仓库相对链接改写为站点内部链接。"""
    def repl(match: re.Match) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        clean = target.split("#", 1)[0]
        anchor = target[len(clean):]
        if not clean:
            return match.group(0)
        resolved = (source.parent / clean).resolve()
        if resolved.suffix == ".md" and resolved.is_file():
            try:
                rel = Path(resolved).relative_to(ROOT).with_suffix(".html")
            except ValueError:
                return match.group(0)
            href = os.path.relpath(rel, source.parent)
            return f"[{label}]({Path(href).as_posix()}{anchor})"
        if not resolved.exists():
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                return match.group(0)  # 指向仓库外（如 ../../actions），原样保留
            return f"{label}（链接失效：{target}）"
        return match.group(0)

    return re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", repl, md_text)


# --------------------------------------------------------------------------- #
# 页面模板
# --------------------------------------------------------------------------- #
def render_nav(current: str) -> str:
    current_dir = Path(current).parent
    parts = ['<nav class="sidebar">']
    for group, items in NAV:
        parts.append('<div class="nav-group">')
        parts.append(f'<div class="nav-group-title">{html.escape(group)}</div>')
        for title, src in items:
            href = os.path.relpath(Path(src).with_suffix(".html"), current_dir)
            active = " active" if src == current else ""
            parts.append(
                f'<a class="nav-item{active}" href="{href}">{html.escape(title)}</a>'
            )
        parts.append("</div>")
    parts.append(
        f'<a class="nav-repo" href="{REPO_URL}" target="_blank" rel="noopener">GitHub 仓库 ↗</a>'
    )
    parts.append("</nav>")
    return "\n".join(parts)


def render_page(title: str, source: str, body: str) -> str:
    nav = render_nav(source)
    depth = len(Path(source).parent.parts)  # README.md 在根目录 → 0
    prefix = "../" * depth
    heading = title
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {SITE_TITLE}</title>
<meta name="description" content="{html.escape(SITE_TAGLINE)}">
<link rel="icon" href="{prefix}assets/logo.svg">
<link rel="stylesheet" href="{prefix}assets/pygments.css">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip-link" href="#content">跳到正文</a>
<header class="topbar">
  <a class="brand" href="{prefix}index.html">
    <img src="{prefix}assets/logo.svg" alt="" width="26" height="26">
    <span>fastfeishu</span>
  </a>
  <span class="topbar-doc">{html.escape(heading)}</span>
</header>
<div class="layout">
{nav}
<main class="content" id="content">
{body}
<hr class="footer-rule">
<p class="footer">由 <code>tools/build_docs_site.py</code> 从 Markdown 生成 · 文档以仓库 <code>docs/</code> 为准</p>
</main>
</div>
<script>
document.querySelectorAll('.content a[href^="#"]').forEach(function (a) {{
  a.addEventListener('click', function () {{
    var el = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
    if (el) el.scrollIntoView({{behavior: 'smooth', block: 'start'}});
  }});
}});
</script>
</body>
</html>
"""


CSS = """/* fastfeishu docs site */
:root {
  --bg: #ffffff;
  --bg-soft: #f7f8fa;
  --bg-code: #f6f8fa;
  --border: #e5e7eb;
  --text: #1f2328;
  --text-soft: #59636e;
  --accent: #2f6feb;
  --accent-soft: #eaf1ff;
  --sidebar-w: 268px;
  --topbar-h: 56px;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117;
    --bg-soft: #161b22;
    --bg-code: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-soft: #9198a1;
    --accent: #6ea8ff;
    --accent-soft: #16243d;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.skip-link { position: absolute; left: -9999px; }
.skip-link:focus { left: 8px; top: 8px; background: var(--bg); padding: 8px; z-index: 10; }

/* top bar */
.topbar {
  position: sticky; top: 0; z-index: 5;
  height: var(--topbar-h);
  display: flex; align-items: center; gap: 14px;
  padding: 0 20px;
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--text); }
.brand:hover { text-decoration: none; }
.topbar-doc { color: var(--text-soft); font-size: 13.5px; }

/* layout */
.layout { display: flex; align-items: flex-start; }
.sidebar {
  position: sticky; top: var(--topbar-h);
  width: var(--sidebar-w); flex: 0 0 var(--sidebar-w);
  height: calc(100vh - var(--topbar-h));
  overflow-y: auto;
  padding: 22px 14px 40px 20px;
  border-right: 1px solid var(--border);
}
.nav-group { margin-bottom: 20px; }
.nav-group-title {
  font-size: 11.5px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--text-soft); margin: 0 0 6px 10px;
}
.nav-item {
  display: block; padding: 6px 10px; border-radius: 7px;
  color: var(--text-soft); font-size: 14px; line-height: 1.5;
}
.nav-item:hover { background: var(--bg-soft); color: var(--text); text-decoration: none; }
.nav-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
.nav-repo {
  display: block; margin: 26px 10px 0; padding-top: 16px;
  border-top: 1px solid var(--border); font-size: 13.5px;
}

/* content */
.content {
  flex: 1 1 auto; min-width: 0; max-width: 900px;
  padding: 34px 40px 80px;
}
.content > h1:first-child { margin-top: 0; }
h1 { font-size: 30px; line-height: 1.3; margin: 0 0 20px; letter-spacing: -.01em; }
h2 {
  font-size: 21px; margin: 40px 0 12px; padding-top: 14px;
  border-top: 1px solid var(--border); letter-spacing: -.01em;
}
/* Markdown 里的 --- 分隔线紧跟 h2 时会与 h2 自身上边框重叠 */
hr + h2 { display: none; }
hr + h2 + * { margin-top: 0; }
h3 { font-size: 17px; margin: 28px 0 8px; }
h4 { font-size: 15.5px; margin: 22px 0 6px; }
p { margin: 10px 0; }
ul, ol { padding-left: 22px; }
li { margin: 4px 0; }
blockquote {
  margin: 14px 0; padding: 10px 16px;
  border-left: 3px solid var(--accent);
  background: var(--bg-soft); border-radius: 0 8px 8px 0; color: var(--text-soft);
}
hr { border: 0; border-top: 1px solid var(--border); margin: 28px 0; }
code {
  font-family: var(--mono); font-size: .875em;
  background: var(--bg-code); padding: .15em .38em; border-radius: 5px;
}
pre {
  background: var(--bg-code); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 16px; overflow-x: auto; line-height: 1.6;
}
pre code, pre code.hljs { background: transparent; padding: 0; font-size: 13px; }
table {
  border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 13.5px;
  display: block; overflow-x: auto;
}
th, td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
th { background: var(--bg-soft); font-weight: 600; }
img { max-width: 100%; }
.footer-rule { margin-top: 56px; }
.footer { color: var(--text-soft); font-size: 13px; }

@media (max-width: 860px) {
  .layout { display: block; }
  .sidebar {
    position: static; width: auto; height: auto;
    border-right: 0; border-bottom: 1px solid var(--border);
    padding: 16px 20px;
  }
  .content { padding: 24px 20px 60px; }
}
"""


def build(out_dir: Path) -> None:
    formatter, md = build_highlighter()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "assets").mkdir(parents=True)

    (out_dir / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    (out_dir / "assets" / "pygments.css").write_text(highlight_css(), encoding="utf-8")
    for svg in ASSETS.glob("*.svg"):
        shutil.copy2(svg, out_dir / "assets" / svg.name)
    if (ROOT / "LICENSE").is_file():      # README 中的许可证链接
        shutil.copy2(ROOT / "LICENSE", out_dir / "LICENSE")

    missing = []
    for title, src in PAGES:
        source = ROOT / src
        if not source.is_file():
            missing.append(src)
            continue
        text = source.read_text(encoding="utf-8")
        text = rewrite_links(text, source)
        tokens = md.parse(text)
        html_out = md.renderer.render(tokens, md.options, {})
        target = out_dir / Path(src).with_suffix(".html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(title, src, html_out), encoding="utf-8")

    index = out_dir / "index.html"
    readme_page = out_dir / "README.html"
    if readme_page.is_file():
        index.write_text(
            readme_page.read_text(encoding="utf-8").replace('href="README.html"', 'href="index.html"'),
            encoding="utf-8",
        )

    if missing:
        print("⚠️  缺失文档：", ", ".join(missing))
    print(f"✅ 已生成 {len(PAGES) - len(missing)} 个页面 → {out_dir}")
    print(f"   本地预览：python -m http.server -d {out_dir} 8000")


def main() -> None:
    parser = argparse.ArgumentParser(description="构建 fastfeishu 文档站点")
    parser.add_argument("--out", default="site", help="输出目录（默认 site/）")
    args = parser.parse_args()
    build((ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out))


if __name__ == "__main__":
    main()
