#!/usr/bin/env python3
# (C) PSK OG Marienheide e.V., VR/Köln 1369
"""Check generated local links and automatic resource URLs, without network access."""

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attribute in ("src", "poster", "srcset", "ping"):
            if attrs.get(attribute):
                value = attrs[attribute]
                if attribute == "srcset":
                    self.links.extend((entry.strip().split()[0], True) for entry in value.split(","))
                else:
                    self.links.append((value, True))
        if attrs.get("href"):
            rel = set(attrs.get("rel", "").split())
            # Canonical metadata is a URL, not a fetched asset.
            if not (tag == "link" and rel == {"canonical"}):
                self.links.append((attrs["href"], tag != "a"))
        if tag == "object" and attrs.get("data"):
            self.links.append((attrs["data"], True))
        if tag in {"iframe", "embed", "object", "base"}:
            raise ValueError(f"Unsupported embedded content or base URL: {tag}")
        if attrs.get("style") or any(key.startswith("on") for key in attrs):
            raise ValueError("Inline styles/scripts are incompatible with the site's CSP")

    def handle_data(self, value):
        self.text.append(value)


def check_migration(output, source_root):
    """Verify source outcomes and the reviewed PDF bytes, including legacy URLs."""
    output, source_root = Path(output), Path(source_root)
    errors = []
    records = json.loads((source_root / "data/migration-pages.json").read_text())
    if len(records) != 27 or len({row["source_id"] for row in records}) != 27:
        errors.append("Migration inventory must account for all 27 distinct source pages/posts")
    for row in records:
        path = output / row["source_path"].lstrip("/") / "index.html"
        if row["outcome"] == "migrated":
            target = output / row["target_path"].lstrip("/") / "index.html"
            if not target.is_file():
                errors.append(f"Migrated source page missing: {row['source_path']}")
            if path != target and not path.is_file():
                errors.append(f"Legacy source page missing: {row['source_path']}")
        elif row["outcome"] != "retired" or path.exists():
            errors.append(f"Retired source page reintroduced or unknown outcome: {row['source_path']}")
    for name in ("impressum", "datenschutz", "downloads"):
        if not (output / name / "index.html").is_file():
            errors.append(f"Required page missing: {name}")
    legal = output / "impressum/index.html"
    if legal.is_file() and not re.search(r"Amtsgericht Köln,\s*VR 1369", legal.read_text()):
        errors.append("Register court/number missing from Impressum")
    for row in json.loads((source_root / "data/downloads.json").read_text()):
        paths = [source_root / row["path"], output / row["url"].lstrip("/")]
        paths.extend(output / url.lstrip("/") for url in row["legacy_urls"])
        for path in paths:
            if not path.is_file():
                errors.append(f"Required download missing: {path}")
                continue
            data = path.read_bytes()
            if not data.startswith(b"%PDF-") or len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                errors.append(f"Download differs from reviewed PDF: {path}")
    for row in json.loads((source_root / "data/migration-assets.json").read_text()):
        path = source_root / row["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            errors.append(f"Migrated asset differs from recorded source: {row['path']}")
    return errors


def check_site(output, base_url, source_root=None):
    output = Path(output).resolve()
    base = urlsplit(base_url)
    if base.scheme not in {"https", "http"} or not base.netloc or not base.path.endswith("/"):
        raise ValueError("BASE_URL must be an absolute HTTP(S) URL ending in /")
    pages = {}
    errors = []
    for file in output.rglob("*"):
        relative = file.relative_to(output)
        if file.is_symlink():
            errors.append(f"{relative}: symbolic links cannot be published")
        if any(part.startswith(".") or part in {"reference", "build", "tools"} for part in relative.parts):
            errors.append(f"{relative}: source/reference material leaked into output")
        if not file.is_file():
            continue
        if file.suffix == ".html":
            page = Page()
            try:
                page.feed(file.read_text())
            except ValueError as error:
                errors.append(f"{relative}: {error}")
            pages[file] = page
            text = " ".join(page.text)
            if re.search(r"WordPress|Dennis\s+Schmidt|0170\s*8082837|Gästebuch|Anmeldung zur KSA|Kalender|Terminschutzantrag", text, re.I):
                errors.append(f"{relative}: retired content is present")
        if file.suffix in {".css", ".js"}:
            text = file.read_text()
            if re.search(r"(?:https?:)?//[\w.-]+", text):
                errors.append(f"{relative}: remote URL in CSS/JavaScript")
            if file.suffix == ".css" and re.search(r"@import\b|url\s*\(", text, re.I):
                errors.append(f"{relative}: CSS resource references need explicit local validation")

    def resolve_link(document, reference, automatic):
        if not reference:
            errors.append(f"{document.relative_to(output)}: empty resource/link")
            return
        relative = document.relative_to(output).as_posix()
        document_url = urljoin(base_url, relative.removesuffix("index.html"))
        target = urlsplit(urljoin(document_url, reference))
        if target.scheme not in {"http", "https"}:
            if automatic or target.scheme not in {"mailto", "tel"}:
                errors.append(f"{relative}: unsupported URL {reference}")
            return
        if (target.scheme, target.netloc) != (base.scheme, base.netloc):
            if automatic:
                errors.append(f"{relative}: external automatic resource {reference}")
            return
        if not target.path.startswith(base.path):
            errors.append(f"{relative}: URL escapes base prefix: {reference}")
            return
        local = output / unquote(target.path[len(base.path):])
        if not local.resolve().is_relative_to(output):
            errors.append(f"{relative}: URL escapes output: {reference}")
            return
        if local.is_dir():
            local = local / "index.html"
        if not local.is_file():
            errors.append(f"{relative}: missing target {reference}")
        elif target.fragment and local in pages and unquote(target.fragment) not in pages[local].ids:
            errors.append(f"{relative}: missing fragment {reference}")

    for file, page in pages.items():
        for reference, automatic in page.links:
            resolve_link(file, reference, automatic)
    if not (output / "index.html").is_file() or not (output / "404.html").is_file():
        errors.append("Homepage or 404 page is missing")
    if source_root is not None:
        errors.extend(check_migration(output, source_root))
    if errors:
        raise ValueError("\n".join(errors))
    print(f"Static checks passed: {len(pages)} HTML pages at {base_url}")


if __name__ == "__main__":
    try:
        check_site(sys.argv[1], sys.argv[2], Path(__file__).resolve().parent.parent)
    except (ValueError, IndexError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
