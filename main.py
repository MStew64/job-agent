import csv
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent


def read_json(filename):
    path = PROJECT_DIR / filename
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def matches_preferences(job, config):
    title = job.get("title", "").lower()
    location = job.get("location", "").lower()

    title_matches = any(
        keyword.lower() in title
        for keyword in config["titles"]
    )

    location_matches = any(
        keyword.lower() in location
        for keyword in config["location_keywords"]
    )

    remote_matches = (
        config["include_remote"]
        and "remote" in location
    )

    return title_matches and (location_matches or remote_matches)


def main():
    config = read_json("config.json")
    jobs = read_json("sample_jobs.json")

    matches = []
    seen_urls = set()

    for job in jobs:
        url = job.get("url", "")

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        if matches_preferences(job, config):
            matches.append(job)

    report_dir = PROJECT_DIR / "reports"
    report_dir.mkdir(exist_ok=True)

    output_path = report_dir / "jobs.csv"
    columns = ["title", "company", "location", "url"]

    with output_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(matches)

    print(f"Checked {len(jobs)} listings.")
    print(f"Found {len(matches)} matching jobs.")
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()