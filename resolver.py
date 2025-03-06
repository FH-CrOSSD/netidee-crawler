#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Annotated, Optional

import typer

app = typer.Typer(rich_markup_mode="markdown")


@app.command()
def main(
    input: Annotated[
        Optional[Path],
        typer.Option(
            "--input",
            "-i",
            help="url file - github urls [default: stdin]",
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
    Takes a list of github URLs and retrieves all repositories of a user/orga in case the URL does not contain the repository portion.
    > Forks are **excluded**.
    """
    regex = re.compile(r"https://github.com/([^/]+)/*([^/?#]*)")

    res = set()

    with open(input) if input else sys.stdin as data:
        for line in data:
            line = line.strip()
            match = re.match(regex, line)
            if not match.groups()[1]:
                with urllib.request.urlopen(
                    f"https://api.github.com/users/{match.groups()[0]}/repos"
                ) as response:
                    data = response.read()
                    json_data = json.loads(data)
                    res |= set(elem["html_url"] for elem in json_data if elem["fork"] == False)
            else:
                res.add(line)

    with open(output, "w") if output else sys.stdout as out:
        out.write("\n".join(res))
        out.write("\n")


if __name__ == "__main__":
    app()
