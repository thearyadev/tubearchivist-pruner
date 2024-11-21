# tubearchivist pruner
the builtin pruner wasnt working. 

this script will delete all videos that are watched and older than a specified number of days 

## Usage
### cli 

can be run with python 3.12

```bash
> python main.py

usage: tubearchivist-pruner [-h] -a MIN_WATCHED_AGE -u URL -t TOKEN [-e]
                            [-s SLEEP]

this script will delete all videos that are watched and older than a specified
number of days

options:
  -h, --help            show this help message and exit
  -a MIN_WATCHED_AGE, --min-watched-age MIN_WATCHED_AGE
                        Min age in days from the watched date
  -u URL, --url URL     Tube archivist API url
  -t TOKEN, --token TOKEN
                        Tube archviist api token
  -e, --endless
  -s SLEEP, --sleep SLEEP
```

### docker (compose)
```yaml
services:
    ta-pruner:
        image: thearyadev0/tubearchivist-pruner:latest # or version tag
        environment:
            TUBEARCHIVIST_URL: ""
            API_TOKEN: ""
            PRUNE_OLDER_THAN: "" # number of days. All videos older than this, that are watched, will be deleted.
            SLEEP: "" # OPTONAL: number of seconds to wait before running again
```

license: wtfpl
