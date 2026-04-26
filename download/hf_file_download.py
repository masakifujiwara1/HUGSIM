import argparse
import zipfile
from pathlib import Path

from huggingface_hub import snapshot_download


SCENE_FOLDERS = ["kitti360", "nuscenes", "pandaset", "waymo"]

def unzip(file):
    file_path = file.as_posix()
    dir_path = file.parent.as_posix()
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

def extract_scene_folders(root_dir: Path = Path("./scenes"), scene_folders=None):
    """
    Recursively extract .zip files under the selected scenes/ subfolders.

    For each zip at e.g. scenes/kitti360/file.zip,
    extract into scenes/kitti360/file/.
    """
    if not root_dir.exists():
        raise FileNotFoundError(f"{root_dir} does not exist")

    search_roots = [root_dir / scene_folder for scene_folder in scene_folders] if scene_folders else [root_dir]
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for zip_path in search_root.rglob("*.zip"):
            print(f"Extracting {zip_path}...")
            unzip(zip_path)


def download_scene_folders(scene_folders):
    for scene_folder in scene_folders:
        print(f"Downloading scenes/{scene_folder}...")
        snapshot_download(
            repo_id='XDimLab/HUGSIM',
            revision='main',
            local_dir='.',
            local_dir_use_symlinks=False,
            allow_patterns=[f'scenes/{scene_folder}/**'],
            repo_type='dataset',
        )


def main():
    parser = argparse.ArgumentParser(description='Download HUGSIM public dataset files.')
    parser.add_argument(
        '--scene-folders',
        nargs='+',
        choices=SCENE_FOLDERS,
        default=SCENE_FOLDERS,
        help='Select one or more scene folders under scenes/. Default: all four folders.',
    )
    args = parser.parse_args()

    print("Loading public dataset")

    snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='.',local_dir_use_symlinks=False,allow_patterns=['3DRealCar/**'],repo_type='dataset')
    snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='.',local_dir_use_symlinks=False,allow_patterns=['nusc_map_cache.zip'],repo_type='dataset')
    snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='./scenarios',local_dir_use_symlinks=False,allow_patterns=['scenarios.zip'],repo_type='dataset')
    download_scene_folders(args.scene_folders)

    unzip(Path("./nusc_map_cache.zip"))
    unzip(Path("./scenarios/scenarios.zip"))
    extract_scene_folders(Path("./scenes"), args.scene_folders)


if __name__ == '__main__':
    main()