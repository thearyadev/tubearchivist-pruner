# tubearchivist pruner
the builtin pruner wasnt working.

this script will delete videos that are older than a specified number of days based on download date.
by default it only deletes videos that are already marked watched.
if `IGNORE_WATCH_STATUS=true`, it deletes old videos regardless of watched state.

## Usage
### cli 

can be run with python 3.12

```bash
> python main.py

usage: tubearchivist-pruner [-h] -a MIN_WATCHED_AGE -u URL -t TOKEN [-e] [-s SLEEP]
                            [-i IGNORE_WATCH_STATUS]

this script will delete watched videos older than a specified number of days
based on download date

options:
  -h, --help            show this help message and exit
  -a MIN_WATCHED_AGE, --min-watched-age MIN_WATCHED_AGE
                        Min age in days from the download date
  -u URL, --url URL     Tube archivist API url
  -t TOKEN, --token TOKEN
                        Tube archviist api token
  -e, --endless
  -s SLEEP, --sleep SLEEP
  -i IGNORE_WATCH_STATUS, --ignore-watch-status IGNORE_WATCH_STATUS
                        Delete videos regardless of watch status (true/false)
```

### docker (compose)
```yaml
services:
    ta-pruner:
        image: thearyadev0/tubearchivist-pruner:latest # or version tag
        environment:
            TUBEARCHIVIST_URL: ""
            API_TOKEN: ""
            PRUNE_OLDER_THAN: "" # number of days since download date
            SLEEP: "" # OPTIONAL: number of seconds to wait before running again
            IGNORE_WATCH_STATUS: "false" # OPTIONAL: true/false
```

on startup the pruner will retry for about 10 seconds while tube archivist comes online before exiting non-zero.

license: wtfpl
