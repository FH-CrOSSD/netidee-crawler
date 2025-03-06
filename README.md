# netidee project crawler

This repository is part of the [CrOSSD 2](https://www.netidee.at/crossd2) project. 

## harvester.py
It collects all projects from [netidee](https://www.netidee.at/) and retrieves the according project details, project results as well as blog entries.

```txt
 Usage: harvester.py [OPTIONS]

 Retrieves information about projects on netidee.at and stores it as json.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output              -o               FILE  output file [default: stdout]                                           │
│ --strict                  --relaxed          stricter regex (do not process github urls with remainder after         │
│                                              repository)                                                             │
│                                              [default: relaxed]                                                      │
│ --install-completion                         Install completion for the current shell.                               │
│ --show-completion                            Show completion for the current shell, to copy it or customize the      │
│                                              installation.                                                           │
│ --help                                       Show this message and exit.                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## arbiter.py
Filters URLs based on preference rules:
1. Use URLs in project results, if available.
2. Use URLs in project details, if available.
3. Check each URL in blog entries, if Jaro similarity of project title and github user/orga or repository name exceeds threshold (>0.8).

```txt
Usage: arbiter.py [OPTIONS]

 Takes crawled netidee projects, selects the github urls to include and writes them out. Searches for URLs in the
 following areas (the first area that yields results is chosen):

  • project results
  • project description
  • blog entries
     • Only if the user or the name part of the github url is similar enough to the project title (uses Jaro)

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --input               -i      FILE  json file - crawled netidee projects [default: stdin]                            │
│ --output              -o      FILE  output file [default: stdout]                                                    │
│ --install-completion                Install completion for the current shell.                                        │
│ --show-completion                   Show completion for the current shell, to copy it or customize the installation. │
│ --help                              Show this message and exit.                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## resolver.py
In case of Github user/organization urls, all repositories of that user/organization might be collected instead.

```txt
 Usage: resolver.py [OPTIONS]

 Takes a list of github URLs and retrieves all repositories of a user/orga in case the URL does not contain the
 repository portion.

 ▌ Forks are excluded.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --input               -i      FILE  url file - github urls [default: stdin]                                          │
│ --output              -o      FILE  output file [default: stdout]                                                    │
│ --install-completion                Install completion for the current shell.                                        │
│ --show-completion                   Show completion for the current shell, to copy it or customize the installation. │
│ --help                              Show this message and exit.                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Usage

Install dependencies with:
```bash
pipenv install
```

Activate virtual environment with:
```bash
pipenv shell
```

All commands can be chained pipe:
```bash
./harvester.py | ./arbiter.py | ./resolver.py -o urls.txt
```

## Acknowledgements

The financial support from Internetstiftung/Netidee is gratefully acknowledged. The mission of Netidee is to support development of open-source tools for more accessible and versatile use of the Internet in Austria.
