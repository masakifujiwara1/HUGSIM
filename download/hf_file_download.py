import zipfile
from pathlib import Path

from huggingface_hub import snapshot_download

def unzip(file):
    file_path = file.as_posix()
    dir_path = file.parent.as_posix()
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

def extract_all_scenes(root_dir: Path = Path("./scenes")):
    """
    Recursively extract all .zip files under scenes/ subfolders.

    For each zip at e.g. scenes/kitti360/file.zip,
    extract into scenes/kitti360/file/.
    """
    if not root_dir.exists():
        raise FileNotFoundError(f"{root_dir} does not exist")

    for zip_path in root_dir.rglob("*.zip"):
        print(f"Extracting {zip_path}...")
        unzip(zip_path)

print("Loading public dataset")

snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='.',local_dir_use_symlinks=False,allow_patterns=['3DRealCar/**'],repo_type='dataset')
snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='.',local_dir_use_symlinks=False,allow_patterns=['nusc_map_cache.zip'],repo_type='dataset')
snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='./scenarios',local_dir_use_symlinks=False,allow_patterns=['scenarios.zip'],repo_type='dataset')
snapshot_download(repo_id='XDimLab/HUGSIM',revision='main',local_dir='.',local_dir_use_symlinks=False,allow_patterns=['scenes/'],repo_type='dataset')

unzip(Path("./nusc_map_cache.zip"))
unzip(Path("./scenarios/scenarios.zip"))
extract_all_scenes(Path("./scenes"))