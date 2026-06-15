# Authoring Workflow

Write tutorial content in `content/*.md`, then regenerate the site with:

```bash
python3 scripts/build_site.py
```

This writes the built site to `_site/`. Edit the Markdown sources instead of the generated HTML.

To rebuild automatically whenever you save a Markdown, template, or stylesheet file, run:

```bash
python3 scripts/watch_site.py
```

This uses a small polling watcher written with the Python standard library, so it does not require `watchexec`, `entr`, or editor plugins.

The repository includes a GitHub Actions workflow that runs this build automatically and publishes `_site/` to GitHub Pages on pushes to `main`.

Current tutorial sources live at:

- `content/part-1-motivations-for-unlearning.md`
- `content/part-2-foundations-formal-definitions-and-algorithms.md`
- `content/part-3-applications-of-example-level-unlearning.md`
- `content/part-4-limitations-and-future-directions-of-example-level-unlearning.md`

## Page Structure

Each content file has YAML front matter:

```yaml
---
part: Part 1
title: Example Title
description: Short page description for metadata.
dek: Short summary shown under the page title.
output: example-page.html
---
```

Then write the page body in Markdown.

## Supported Markdown

- `##` and `###` headings
- paragraphs
- ordered and unordered lists
- blockquotes with `>`
- horizontal rules with `---`
- links like `[text](https://example.com)`
- inline code with backticks
- emphasis with `*text*` and `**text**`

## Anchors and Table of Contents

Add explicit heading ids so the right-hand table of contents stays stable:

```md
## Overview {#overview}
### Privacy and Data Rights {#privacy}
```

## Citations

Inline citations use:

```md
This is a claim.[@gdpr-2016]
```

Use stable semantic keys instead of sequential numbers. The built site renders
citations as `[1]`, `[2]`, and so on based on first appearance, while linking
to the matching reference entry.

## References

Give each reference list item an id:

```md
## References {#references}

1. {#gdpr-2016} European Union. General Data Protection Regulation, 2016.
2. {#cauwenberghs-poggio-2000} Cauwenberghs and Poggio. Incremental and Decremental SVM Learning, 2000.
```

Within the `## References {#references}` section, the source order does not
need to match citation order. The builder automatically reorders cited entries
to match first appearance and leaves uncited entries after them.

## Recommended Writing Loop

1. Edit one `content/*.md` file.
2. Run `python3 scripts/watch_site.py`.
3. Leave the watcher running while you write.
4. Refresh `_site/index.html` after each save.
