#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import parse_qs, urlparse

import typer
from bs4 import BeautifulSoup

app = typer.Typer(rich_markup_mode="markdown")


@app.command()
def main(
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="output file [default: stdout]",
            file_okay=True,
            dir_okay=False,
            writable=True,
            show_default=False,
        ),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict/--relaxed",
            help="stricter regex (do not process github urls with remainder after repository)",
            is_flag=True,
        ),
    ] = False,
):
    """
    Retrieves information about projects on netidee.at and stores it as json.
    """
    reg_info = re.compile(r"[^0-9]+(\d+)[^0-9]+(\d+)[^0-9]*(\d*)")
    reg_strict = re.compile(r"https://github.com/([^/]+)/*([^/?#]*)/?$")
    reg_relaxed = re.compile(r"https://github.com/([^/]+)/*([^/?#]*)")
    regex = reg_relaxed
    if strict:
        regex = reg_strict

    # URL of the webpage to scrape
    url = "https://www.netidee.at/entdecken?type=project"

    # Send a GET request to fetch the webpage content
    response = urllib.request.urlopen(url)

    # Parse the webpage content using BeautifulSoup
    soup = BeautifulSoup(response.read(), "html.parser")

    results = {}

    projects = []
    # Find all anchor tags and extract href attributes
    projects += [project["href"] for project in soup.css.select('a[data-category="projects"]')]

    lastpage = parse_qs(urlparse(soup.css.select(".pager__item--last")[0].a["href"]).query)["page"][
        0
    ]

    for page in range(1, int(lastpage) + 1):
        response = urllib.request.urlopen(url + "&page=" + str(page))
        soup = BeautifulSoup(response.read(), "html.parser")
        projects += [project["href"] for project in soup.css.select('a[data-category="projects"]')]

    for project in projects:
        purl = "https://www.netidee.at" + project
        response = urllib.request.urlopen(purl)
        soup = BeautifulSoup(response.read(), "html.parser")
        title = soup.css.select(".description-block--headline")[0].text.strip()
        info = soup.css.select(".description-block--subinfo")[0].text.strip()
        year = call = id = None
        try:
            year, call, id = re.match(
                reg_info,
                soup.css.select(".description-block--subinfo")[0].text.strip(),
            ).groups()
        except AttributeError:
            pass
        pr = set()
        try:
            pr = set(
                x.group()
                for x in filter(
                    None,
                    [
                        re.match(regex, item["href"])
                        for item in soup.css.select(".project-results")[0].find_all("a")
                    ],
                )
            )
        except IndexError:
            pass
        pd = set()
        try:
            pd = set(
                x.group()
                for x in filter(
                    None,
                    [
                        re.match(regex, item["href"])
                        for item in soup.css.select(".project-details")[0].find_all("a")
                    ],
                )
            )
        except IndexError:
            pass

        blogs = [item["href"] for item in soup.css.select('a[data-category-name="Blog"]')]
        blog_links = set()
        for blog in blogs:
            response = urllib.request.urlopen("https://www.netidee.at" + blog)
            soup = BeautifulSoup(response.read(), "html.parser")
            blog_links |= set(
                x.group()
                for x in filter(
                    None,
                    [
                        re.match(regex, item.attrs.get("href", ""))
                        for item in soup.css.select(".blog-content")[0].find_all("a")
                    ],
                )
            )

        results[project] = {
            "url": purl,
            "title": title,
            "project-results": list(pr),
            "info": info,
            "year": year,
            "call": call,
            "id": id,
            "project-details": list(pd),
            "blog-content": list(blog_links),
        }

    with open(output, "w") if output else sys.stdout as out:
        out.write(json.dumps(results, indent=4))


if __name__ == "__main__":
    app()
