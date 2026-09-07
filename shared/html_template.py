"""
Shared HTML report generator.
Pure string generation — no external CSS/JS files.
Responsive + dark-mode friendly.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import html


def _escape(s: Any) -> str:
    return html.escape(str(s))


def generate_html_report(
    title: str,
    sections: List[Dict[str, Any]],
    subtitle: Optional[str] = None,
) -> str:
    """Generate a complete standalone HTML page."""
    css = """
    :root {
        --bg: #0f1117; --surface: #1a1d27; --text: #e6e8ef; --muted: #9aa0b4;
        --accent: #6c9eff; --success: #3dd68c; --warning: #f5a524; --border: #2a2e3b;
    }
    @media (prefers-color-scheme: light) {
        :root {
            --bg: #f7f8fc; --surface: #ffffff; --text: #1a1d27; --muted: #5c6370;
            --accent: #3b6fd9; --success: #0d9f6e; --warning: #c47d00; --border: #e2e5ef;
        }
    }
    * { box-sizing: border-box; }
    body {
        margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: var(--bg); color: var(--text); line-height: 1.55; padding: 1.5rem;
    }
    .container { max-width: 960px; margin: 0 auto; }
    h1 { font-size: 1.75rem; margin: 0 0 0.25rem; }
    .subtitle { color: var(--muted); margin-bottom: 2rem; }
    section {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1.25rem;
    }
    h2 { font-size: 1.2rem; margin: 0 0 0.75rem; color: var(--accent); }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin: 0.75rem 0; }
    th, td { text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--border); }
    th { color: var(--muted); font-weight: 600; }
    tr:last-child td { border-bottom: none; }
    pre, code { font-family: "SF Mono", Consolas, monospace; font-size: 0.85rem; }
    pre {
        background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
        padding: 0.9rem 1rem; overflow-x: auto;
    }
    footer { margin-top: 2rem; color: var(--muted); font-size: 0.8rem; text-align: center; }
    """

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_escape(title)}</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        f"<h1>{_escape(title)}</h1>",
    ]

    if subtitle:
        parts.append(f'<p class="subtitle">{_escape(subtitle)}</p>')

    for sec in sections:
        parts.append("<section>")
        parts.append(f"<h2>{_escape(sec.get('heading', ''))}</h2>")

        body = sec.get("body")
        if isinstance(body, str):
            parts.append(body)
        elif isinstance(body, list):
            for p in body:
                parts.append(f"<p>{_escape(p)}</p>")

        table = sec.get("table")
        if table and len(table) > 0:
            parts.append("<table><thead><tr>")
            for cell in table[0]:
                parts.append(f"<th>{_escape(cell)}</th>")
            parts.append("</tr></thead><tbody>")
            for row in table[1:]:
                parts.append("<tr>")
                for cell in row:
                    parts.append(f"<td>{_escape(cell)}</td>")
                parts.append("</tr>")
            parts.append("</tbody></table>")

        code = sec.get("code")
        if code:
            parts.append(f"<pre><code>{_escape(code)}</code></pre>")

        parts.append("</section>")

    parts.extend([
        "<footer>LQE Ecosystem · pure where possible · honest limitations</footer>",
        "</div></body></html>",
    ])

    return "\n".join(parts)
