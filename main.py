import argparse
import logging
import typing
import datetime
import time

import requests

LIST_VIDEOS_PATH = "/api/video/"
DELETE_VIDEO_PATH = "/api/video/%s/"
IGNORE_VIDEO_PATH = "/api/download/%s/"
STARTUP_GRACE_PERIOD_SECONDS = 10
STARTUP_RETRY_INTERVAL_SECONDS = 1
type Video = dict[str, typing.Any]
type VideoArray = list[Video]


def fetch_all_videos(api_url: str, api_key: str) -> VideoArray:
    headers = {"Authorization": f"Token {api_key}"}
    videos: list[dict] = list()
    page = 1
    last_page_reached = True
    while last_page_reached:
        logging.info(f"Fetching {page=} from tube archivist")
        request = requests.get(
            url=f"{api_url}{LIST_VIDEOS_PATH}?page={page}", headers=headers
        )
        if request.status_code != 200:
            logging.error(
                "Recieved non-200 status code from Tube archivist when fetching video lists"
            )
            logging.error(request.content)
            raise Exception("Failed to reach tubearchivist")
        if len(content := request.json()["data"]) != 0:
            videos.extend(content)
            page += 1
            continue
        last_page_reached = False
    return videos


def delete_video(video: Video, api_url: str, api_key: str) -> None:
    headers = {"Authorization": f"Token {api_key}"}
    url = f"{api_url}{DELETE_VIDEO_PATH % video.get('youtube_id')}"
    logging.info(f"Deleting: {url.replace('/api', '')}")
    request = requests.delete(url, headers=headers)
    if not 200 <= request.status_code < 300:
        logging.error("Recieved non-2xx status code from Tube archivist when deleting")
    return None


def ignore_video(video: Video, api_url: str, api_key: str) -> None:
    headers = {"Authorization": f"Token {api_key}"}
    url = f"{api_url}{IGNORE_VIDEO_PATH% video.get('youtube_id')}"
    logging.info(f"Ignoring: {url.replace('/api', '')}")
    request = requests.post(url, headers=headers, json={"status": "ignore-force"})
    if request.status_code != 200:
        logging.error("Recieved non-200 status code from Tube archivist when ignoring")
    return None


def filter_watched(videos: VideoArray) -> VideoArray:
    return [v for v in videos if v["player"]["watched"] == True]


def filter_watched_date(videos: VideoArray, cutoff: datetime.datetime) -> VideoArray:
    return [
        v
        for v in videos
        if datetime.datetime.fromtimestamp(v["date_downloaded"]) < cutoff
    ]


def str_to_bool(value: str) -> bool:
    if value.lower() in ("true", "1", "yes"):
        return True
    elif value.lower() in ("false", "0", "no"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def prune(
    api_url: str,
    min_age: int,
    api_key: str,
    ignore_watch_status: bool = False,
) -> None:
    videos = fetch_all_videos(api_url, api_key)
    logging.info(f"Found {len(videos)} videos. Filtering age and watch status...")

    if not ignore_watch_status:
        videos = filter_watched(videos)

    videos = filter_watched_date(
        videos, cutoff=datetime.datetime.now() - datetime.timedelta(days=min_age)
    )
    logging.info(f"Filtered results to {len(videos)} videos.")
    for v in videos:
        ignore_video(v, api_url, api_key)
        time.sleep(0.3)
        delete_video(v, api_url, api_key)


def run_with_startup_retry(action_name: str, action: typing.Callable[[], None]) -> None:
    deadline = time.monotonic() + STARTUP_GRACE_PERIOD_SECONDS
    attempt = 1
    while True:
        try:
            action()
            return
        except Exception as err:
            if time.monotonic() >= deadline:
                logging.error(
                    "%s failed during startup for %s seconds, exiting.",
                    action_name,
                    STARTUP_GRACE_PERIOD_SECONDS,
                )
                raise

            logging.warning(
                "%s startup attempt %s failed: %s. Retrying in %s second(s).",
                action_name,
                attempt,
                err,
                STARTUP_RETRY_INTERVAL_SECONDS,
            )
            attempt += 1
            time.sleep(STARTUP_RETRY_INTERVAL_SECONDS)



def main() -> int:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        prog="tubearchivist-pruner",
        description="this script will delete watched videos older than a specified number of days based on download date",
    )

    parser.add_argument(
        "-a",
        "--min-watched-age",
        required=True,
        type=int,
        help="Min age in days from the download date",
    )
    parser.add_argument(
        "-u", "--url", required=True, type=str, help="Tube archivist API url"
    )
    parser.add_argument(
        "-t", "--token", type=str, required=True, help="Tube archviist api token"
    )
    parser.add_argument("-e", "--endless", action="store_true")
    parser.add_argument("-s", "--sleep", type=int, required=False, default=10)
    parser.add_argument(
        "-i",
        "--ignore-watch-status",
        type=str_to_bool,
        default=False,
        help="Delete videos regardless of watch status (true/false)",
    )
    args = parser.parse_args()

    run_with_startup_retry(
        "Pruner",
        lambda: prune(
            api_url=args.url,
            min_age=args.min_watched_age,
            api_key=args.token,
            ignore_watch_status=args.ignore_watch_status,
        ),
    )

    if not args.endless:
        return 0

    while True:
        logging.info(f"running endless... sleeping for {args.sleep} seconds")
        time.sleep(args.sleep)
        prune(
            api_url=args.url,
            min_age=args.min_watched_age,
            api_key=args.token,
            ignore_watch_status=args.ignore_watch_status,
        )


if __name__ == "__main__":
    raise SystemExit(main())
