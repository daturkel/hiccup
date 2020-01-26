from html import unescape
from typing import Tuple

import marko
import frontmatter
import smartypants


def _parse_markdown(text: str) -> str:
    content = unescape(smartypants.convert_quotes(text))
    html_content = marko.convert(content).rstrip()
    return html_content


def _parse_markdown_with_fm(text: str) -> Tuple[dict, str]:
    metadata, content = frontmatter.parse(text)
    return metadata, _parse_markdown(content)


def parse_markdown_file(filename: str) -> str:
    with open(filename, "r") as f:
        html_content = _parse_markdown(f.read())
    return html_content


def parse_markdown_file_with_fm(filename: str) -> Tuple[dict, str]:
    with open(filename, "r") as f:
        metadata, html_content = _parse_markdown_with_fm(f.read())
    return metadata, html_content
