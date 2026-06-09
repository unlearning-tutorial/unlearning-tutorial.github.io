#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import html
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
TEMPLATE_PATH = ROOT / "templates" / "article.html"
STATIC_FILES = ("index.html", "styles.css", "article.css")

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ID_SUFFIX_RE = re.compile(r"^(.*?)\s*\{#([A-Za-z0-9_-]+)\}\s*$")
UL_RE = re.compile(r"^[-*]\s+(.+)$")
OL_RE = re.compile(r"^\d+\.\s+(.+)$")
REF_ITEM_RE = re.compile(r"^\{#([A-Za-z0-9_-]+)\}\s*(.+)$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
STRONG_RE = re.compile(r"\*\*(.+?)\*\*")
EM_RE = re.compile(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)")
CODE_RE = re.compile(r"`([^`]+)`")
CITATION_RE = re.compile(r"\[@([A-Za-z0-9_-]+)\]")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("Expected YAML front matter at top of file.")

    _, rest = text.split("---\n", 1)
    front_matter, body = rest.split("\n---\n", 1)
    metadata = yaml.safe_load(front_matter) or {}
    return metadata, body.strip() + "\n"


def format_citation_label(ref_id: str) -> str:
    match = re.fullmatch(r"ref-(.+)", ref_id)
    if match:
        return match.group(1)
    return ref_id


def render_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = CITATION_RE.sub(
        lambda m: (
            f'<a class="citation" href="#{html.escape(m.group(1))}">'
            f'[{html.escape(format_citation_label(m.group(1)))}]</a>'
        ),
        escaped,
    )
    escaped = LINK_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    escaped = CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", escaped)
    escaped = STRONG_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", escaped)
    escaped = EM_RE.sub(lambda m: f"<em>{m.group(1)}</em>", escaped)
    return escaped


def extract_heading_data(raw_text: str) -> tuple[str, str]:
    match = ID_SUFFIX_RE.match(raw_text)
    if match:
        return match.group(1).strip(), match.group(2)
    clean = raw_text.strip()
    return clean, slugify(clean)


def render_markdown(markdown_text: str) -> tuple[str, list[dict[str, str | int]]]:
    lines = markdown_text.splitlines()
    toc: list[dict[str, str | int]] = []
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    quote_lines: list[str] = []
    list_type: str | None = None
    list_items: list[tuple[str, str | None]] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            text = " ".join(line.strip() for line in paragraph_lines)
            blocks.append(f"<p>{render_inline(text)}</p>")
            paragraph_lines = []

    def flush_quote() -> None:
        nonlocal quote_lines
        if quote_lines:
            text = " ".join(line.strip() for line in quote_lines)
            blocks.append(f"<blockquote><p>{render_inline(text)}</p></blockquote>")
            quote_lines = []

    def flush_list() -> None:
        nonlocal list_type, list_items
        if not list_type:
            return

        tag = "ul" if list_type == "ul" else "ol"
        rendered_items = []
        for item_text, item_id in list_items:
            id_attr = f' id="{html.escape(item_id, quote=True)}"' if item_id else ""
            rendered_items.append(
                f"  <li{id_attr}>{render_inline(item_text.strip())}</li>"
            )
        blocks.append(f"<{tag}>\n" + "\n".join(rendered_items) + f"\n</{tag}>")
        list_type = None
        list_items = []

    def flush_all() -> None:
        flush_paragraph()
        flush_quote()
        flush_list()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_all()
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            flush_all()
            level = len(heading_match.group(1))
            heading_text, heading_id = extract_heading_data(heading_match.group(2))
            if level in (2, 3):
                toc.append({"level": level, "id": heading_id, "text": heading_text})
            blocks.append(
                f'<h{level} id="{html.escape(heading_id, quote=True)}">'
                f"{render_inline(heading_text)}</h{level}>"
            )
            continue

        if re.fullmatch(r"-{3,}", stripped):
            flush_all()
            blocks.append("<hr />")
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            quote_lines.append(stripped[1:].lstrip())
            continue

        ul_match = UL_RE.match(stripped)
        if ul_match:
            flush_paragraph()
            flush_quote()
            if list_type not in (None, "ul"):
                flush_list()
            list_type = "ul"
            item_text = ul_match.group(1)
            item_id = None
            ref_match = REF_ITEM_RE.match(item_text)
            if ref_match:
                item_id = ref_match.group(1)
                item_text = ref_match.group(2)
            list_items.append((item_text, item_id))
            continue

        ol_match = OL_RE.match(stripped)
        if ol_match:
            flush_paragraph()
            flush_quote()
            if list_type not in (None, "ol"):
                flush_list()
            list_type = "ol"
            item_text = ol_match.group(1)
            item_id = None
            ref_match = REF_ITEM_RE.match(item_text)
            if ref_match:
                item_id = ref_match.group(1)
                item_text = ref_match.group(2)
            list_items.append((item_text, item_id))
            continue

        flush_quote()
        flush_list()
        paragraph_lines.append(stripped)

    flush_all()
    return "\n".join(blocks), toc


def render_toc(toc: list[dict[str, str | int]]) -> str:
    items = []
    for entry in toc:
        level_class = " toc-subitem" if entry["level"] == 3 else ""
        items.append(
            '            <li class="toc-item{cls}"><a href="#{id}">{text}</a></li>'.format(
                cls=level_class,
                id=html.escape(str(entry["id"]), quote=True),
                text=html.escape(str(entry["text"])),
            )
        )
    return "\n".join(items)


def build_page(source_path: Path, template: str, output_dir: Path) -> None:
    metadata, markdown_body = parse_front_matter(source_path.read_text())
    body_html, toc = render_markdown(markdown_body)
    output_name = metadata["output"]
    output_path = output_dir / output_name

    page = template
    replacements = {
        "{{TITLE}}": html.escape(metadata["title"]),
        "{{DESCRIPTION}}": html.escape(metadata["description"], quote=True),
        "{{PART}}": html.escape(metadata["part"]),
        "{{DEK}}": html.escape(metadata["dek"]),
        "{{BODY}}": "\n".join(f"          {line}" if line else "" for line in body_html.splitlines()),
        "{{TOC}}": render_toc(toc),
    }

    for key, value in replacements.items():
        page = page.replace(key, value)

    generated = (
        f"<!-- Generated from {source_path.relative_to(ROOT)} by scripts/build_site.py -->\n"
        f"{page}\n"
    )
    output_path.write_text(generated)


def copy_static_files(output_dir: Path) -> None:
    for filename in STATIC_FILES:
        shutil.copy2(ROOT / filename, output_dir / filename)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tutorial site pages from Markdown.")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the generated site should be written.",
    )
    parser.add_argument(
        "--skip-static",
        action="store_true",
        help="Do not copy index.html and CSS assets to the output directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE_PATH.read_text()
    if not args.skip_static:
        copy_static_files(output_dir)
    for source_path in sorted(CONTENT_DIR.glob("*.md")):
        build_page(source_path, template, output_dir)


if __name__ == "__main__":
    main()
