#!/usr/bin/env python3
"""Validate Senel's search and sharing metadata without third-party packages."""

from html.parser import HTMLParser
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
LIVE_URL = "https://throwingogo-hub.github.io/senel/"


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_json_ld = False
        self.json_ld = ""
        self.canonical = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href") or ""
        if tag == "script" and values.get("type") == "application/ld+json":
            self.in_json_ld = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_json_ld:
            self.json_ld += data


html = (ROOT / "docs/index.html").read_text()
parser = MetadataParser()
parser.feed(html)
assert parser.canonical == LIVE_URL
structured = json.loads(parser.json_ld)
assert structured["@type"] == "WebApplication"
assert structured["url"] == LIVE_URL
assert structured["offers"]["price"] == "0"

robots = (ROOT / "docs/robots.txt").read_text()
assert f"Sitemap: {LIVE_URL}sitemap.xml" in robots
tree = ET.parse(ROOT / "docs/sitemap.xml")
locations = {node.text for node in tree.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
assert locations == {LIVE_URL}

print("PASS: Senel canonical, structured data, robots.txt, and sitemap.xml")
