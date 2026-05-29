#!/usr/bin/env python3
"""List nuScenes scenes usable by data/nusc/load.py.

The ASAP-generated interp_12Hz_trainval metadata can contain scenes whose
first_sample_token is not present in sample.json.  load.py resolves a scene by
name and immediately loads that first sample, so those scenes are not usable by
the current loader.

Examples:
    python HUGSIM/data/nusc/list_available_scenes.py
    python HUGSIM/data/nusc/list_available_scenes.py --format csv --out available_scenes.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path


AVAILABLE_CAMERAS = (
    "CAM_FRONT",
    "CAM_FRONT_LEFT",
    "CAM_FRONT_RIGHT",
    "CAM_BACK_LEFT",
    "CAM_BACK_RIGHT",
    "CAM_BACK",
)
FIRST_SAMPLE_SENSORS = ("LIDAR_TOP",) + AVAILABLE_CAMERAS


def default_dataroot() -> Path:
    return Path(__file__).resolve().parents[2] / "download" / "data" / "nuscenes"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print scene names available in a nuScenes metadata version."
    )
    parser.add_argument(
        "--datapath",
        type=Path,
        default=default_dataroot(),
        help="nuScenes dataroot. Defaults to HUGSIM/download/data/nuscenes.",
    )
    parser.add_argument(
        "--version",
        default="interp_12Hz_trainval",
        help="Metadata folder under --datapath. Case-insensitive fallback is supported.",
    )
    parser.add_argument(
        "--check-files",
        choices=("none", "first", "all"),
        default="first",
        help=(
            "File existence check level: none only checks sample metadata, "
            "first checks first-sample LiDAR and camera files, all checks the "
            "selected camera frames plus the first-sample LiDAR/camera files."
        ),
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index for the sample chain. Matches nusc/load.py.",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=-1,
        help="End index for the sample chain. Matches nusc/load.py.",
    )
    parser.add_argument(
        "--format",
        choices=("plain", "csv", "json"),
        default="plain",
        help="Output format. plain prints one scene name per line.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional output file. Defaults to stdout.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a short availability summary to stderr.",
    )
    parser.add_argument(
        "--include-unavailable",
        action="store_true",
        help="Include unavailable scenes in csv/json output with status and reason.",
    )
    return parser.parse_args()


def resolve_version_dir(dataroot: Path, version: str) -> Path:
    version_dir = dataroot / version
    if version_dir.is_dir():
        return version_dir

    if dataroot.is_dir():
        version_lower = version.lower()
        for child in dataroot.iterdir():
            if child.is_dir() and child.name.lower() == version_lower:
                return child

    raise FileNotFoundError(f"Metadata version directory not found: {version_dir}")


def load_table(version_dir: Path, table_name: str) -> list[dict]:
    table_path = version_dir / f"{table_name}.json"
    if not table_path.is_file():
        raise FileNotFoundError(f"Required metadata table not found: {table_path}")
    with table_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def walk_samples(first_token: str, samples_by_token: dict[str, dict]) -> tuple[list[dict], str]:
    samples = []
    seen = set()
    token = first_token

    while token:
        if token in seen:
            return samples, f"sample chain has a cycle at token {token}"
        seen.add(token)

        sample = samples_by_token.get(token)
        if sample is None:
            return samples, f"sample token not found: {token}"

        samples.append(sample)
        token = sample.get("next", "")

    return samples, ""


def check_sensor_tokens(
    all_samples: list[dict],
    selected_samples: list[dict],
    sample_data_by_token: dict[str, dict],
    check_files: str,
    dataroot: Path,
) -> str:
    if not all_samples:
        return "no reachable samples"
    if not selected_samples:
        return "selected sample slice is empty"

    first_sample = all_samples[0]
    for sensor in FIRST_SAMPLE_SENSORS:
        data_token = first_sample.get("data", {}).get(sensor)
        if data_token is None:
            return f"first sample is missing sensor {sensor}"
        sample_data = sample_data_by_token.get(data_token)
        if sample_data is None:
            return f"sample_data token not found for {sensor}: {data_token}"
        if check_files in {"first", "all"}:
            filename = sample_data.get("filename")
            if not filename:
                return f"sample_data filename is empty for {sensor}: {data_token}"
            if not (dataroot / filename).is_file():
                return f"file not found for {sensor}: {filename}"

    if check_files != "all":
        return ""

    for sample in selected_samples:
        for camera in AVAILABLE_CAMERAS:
            data_token = sample.get("data", {}).get(camera)
            if data_token is None:
                return f"sample {sample.get('token')} is missing sensor {camera}"
            sample_data = sample_data_by_token.get(data_token)
            if sample_data is None:
                return f"sample_data token not found for {camera}: {data_token}"
            filename = sample_data.get("filename")
            if not filename:
                return f"sample_data filename is empty for {camera}: {data_token}"
            if not (dataroot / filename).is_file():
                return f"file not found for {camera}: {filename}"

    return ""


def collect_scenes(args: argparse.Namespace, version_dir: Path) -> list[dict]:
    scenes = load_table(version_dir, "scene")
    samples = load_table(version_dir, "sample")
    samples_by_token = {sample["token"]: sample for sample in samples}

    sample_data_by_token = {}
    if args.check_files != "none":
        sample_data = load_table(version_dir, "sample_data")
        sample_data_by_token = {item["token"]: item for item in sample_data}

    rows = []
    for scene in scenes:
        reachable_samples, chain_error = walk_samples(
            scene["first_sample_token"], samples_by_token
        )
        selected_samples = reachable_samples[args.start : args.end]
        reason = chain_error
        if not reason and not selected_samples:
            reason = "selected sample slice is empty"

        if not reason and args.check_files != "none":
            reason = check_sensor_tokens(
                reachable_samples,
                selected_samples,
                sample_data_by_token,
                args.check_files,
                args.datapath,
            )

        rows.append(
            {
                "name": scene["name"],
                "status": "available" if not reason else "unavailable",
                "sample_count": len(reachable_samples),
                "selected_sample_count": len(selected_samples),
                "scene_nbr_samples": scene.get("nbr_samples", ""),
                "description": scene.get("description", ""),
                "reason": reason,
            }
        )

    return rows


def write_plain(rows: list[dict], out_file) -> None:
    for row in rows:
        if row["status"] == "available":
            print(row["name"], file=out_file)


def write_csv(rows: list[dict], out_file) -> None:
    fieldnames = (
        "name",
        "status",
        "sample_count",
        "selected_sample_count",
        "scene_nbr_samples",
        "description",
        "reason",
    )
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def write_json(rows: list[dict], out_file) -> None:
    json.dump(rows, out_file, indent=2)
    print(file=out_file)


def main() -> int:
    args = parse_args()
    args.datapath = args.datapath.resolve()
    version_dir = resolve_version_dir(args.datapath, args.version)

    rows = collect_scenes(args, version_dir)
    if not args.include_unavailable:
        rows = [row for row in rows if row["status"] == "available"]

    if args.out is None:
        out_file = sys.stdout
        close_out = False
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        out_file = args.out.open("w", encoding="utf-8", newline="")
        close_out = True

    try:
        if args.format == "plain":
            write_plain(rows, out_file)
        elif args.format == "csv":
            write_csv(rows, out_file)
        else:
            write_json(rows, out_file)
    finally:
        if close_out:
            out_file.close()

    if args.summary:
        total_scenes = len(load_table(version_dir, "scene"))
        available = sum(1 for row in rows if row["status"] == "available")
        print(
            f"{version_dir.name}: {available}/{total_scenes} scenes available "
            f"(check-files={args.check_files}, start={args.start}, end={args.end})",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
