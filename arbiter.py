#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import json
import re
import sys
from pathlib import Path
from typing import Annotated, Optional

import jellyfish
import typer

app = typer.Typer(rich_markup_mode="markdown")


@app.command()
def main(
    input: Annotated[
        Optional[Path],
        typer.Option(
            "--input",
            "-i",
            help="json file - crawled netidee projects [default: stdin]",
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
        ),
    ] = None,
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
):
    """
    Takes crawled netidee projects, selects the github urls to include and writes them out.
    Searches for URLs in the following areas (the first area that yields results is chosen):
    - project results
    - project description
    - blog entries
        - Only if the user or the name part of the github url is similar enough to the project title (uses Jaro)

    """
    regex = re.compile(r"https://github.com/([^/]+)/*([^/?#]*)")

    data = None
    if not input:
        data = json.loads(sys.stdin.read())
    else:
        with open(input) as content:
            data = json.loads(content.read())

    res = set()
    for project in data:
        if data[project]["project-results"]:
            res |= set(data[project]["project-results"])
        elif data[project]["project-details"]:
            res |= set(data[project]["project-details"])
        else:
            for elem in data[project]["blog-content"]:
                match = re.match(regex, elem)
                if (
                    jellyfish.jaro_similarity(data[project]["title"].lower(), match.groups()[0])
                    > 0.8
                    or jellyfish.jaro_similarity(data[project]["title"].lower(), match.groups()[1])
                    > 0.8
                ):
                    res.add(elem)

    with open(output, "w") if output else sys.stdout as out:
        out.write("\n".join(res))
        out.write("\n")


if __name__ == "__main__":
    # typer.run()
    app()
