#!/usr/bin/env python3
"""Validate the public SEO contract for the Opifer calculator."""

from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "https://calculator.opiferai.com/"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.metas = []
        self.canonicals = []
        self.schemas = []
        self.in_schema = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.metas.append(values)
        elif tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonicals.append(values.get("href", ""))
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self.in_schema = True
            self.schemas.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_schema:
            self.in_schema = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_schema:
            self.schemas[-1] += data


def meta(parser, key, value):
    return [item.get("content", "") for item in parser.metas if item.get(key, "").lower() == value]


def main():
    errors = []
    parser = Parser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

    if not parser.title.strip():
        errors.append("index.html: missing title")
    descriptions = meta(parser, "name", "description")
    if len(descriptions) != 1 or not descriptions[0].strip():
        errors.append("index.html: exactly one meta description is required")
    robots = meta(parser, "name", "robots")
    if robots != ["index, follow"]:
        errors.append("index.html: robots must be exactly index, follow")
    if parser.canonicals != [CANONICAL]:
        errors.append(f"index.html: canonical must be exactly {CANONICAL}")
    for property_name in ("og:title", "og:description", "og:url", "og:image"):
        if len(meta(parser, "property", property_name)) != 1:
            errors.append(f"index.html: exactly one {property_name} tag is required")
    if meta(parser, "name", "twitter:card") != ["summary_large_image"]:
        errors.append("index.html: twitter:card must be summary_large_image")
    if not (ROOT / "og-calculator.png").is_file():
        errors.append("og-calculator.png: missing social sharing image")
    if len(parser.schemas) != 1:
        errors.append("index.html: exactly one JSON-LD schema block is required")
    else:
        try:
            schema = json.loads(parser.schemas[0])
            if schema.get("@type") != "WebApplication" or schema.get("url") != CANONICAL:
                errors.append("index.html: schema must describe the canonical WebApplication")
        except json.JSONDecodeError as exc:
            errors.append(f"index.html: invalid JSON-LD: {exc}")

    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://calculator.opiferai.com/sitemap.xml" not in robots_text:
        errors.append("robots.txt: missing production sitemap declaration")
    if "Disallow: /" in robots_text:
        errors.append("robots.txt: calculator cannot block the whole site")

    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text.strip() for node in tree.findall("sm:url/sm:loc", ns) if node.text]
        if urls != [CANONICAL]:
            errors.append("sitemap.xml: must contain only the canonical calculator URL")
    except ET.ParseError as exc:
        errors.append(f"sitemap.xml: invalid XML: {exc}")

    if errors:
        print("SEO validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SEO validation passed for the Opifer calculator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
