import os
import numpy as np
from pathlib import Path
import argparse
import json
import shutil
from colmap.colmap import COLMAPAuto, rotmat2qvec


def get_opts():
    parser = argparse.ArgumentParser("colmap prepare", description='prepare colamp image dataset')
    parser.add_argument('-i', '--in_path', type=str, required=True)
    return parser.parse_args()

def image_name_from_frame(frame, in_path):
    img_path = os.path.normpath(frame['rgb_path'])
    image_root = os.path.normpath(os.path.join(in_path, 'images'))

    if os.path.isabs(img_path):
        return os.path.relpath(img_path, image_root)
    if img_path == 'images' or img_path.startswith(f'images{os.sep}'):
        return os.path.relpath(img_path, 'images')
    if img_path == f'.{os.sep}images' or img_path.startswith(f'.{os.sep}images{os.sep}'):
        return os.path.relpath(img_path, f'.{os.sep}images')
    return img_path

def write_prior_model(args, meta_data, auto):
    image_metadata = auto.image_metadata_in_database()
    path_prior = os.path.join(args.in_path, 'prior')
    os.makedirs(path_prior, exist_ok=True)

    # points3D
    Path(os.path.join(path_prior, 'points3D.txt')).touch()

    camera_frames = {}
    with open(os.path.join(path_prior, 'images.txt'), 'w') as f:
        for frame in meta_data['frames']:
            c2w = np.array(frame['camtoworld'])
            image_name = image_name_from_frame(frame, args.in_path)

            if image_name not in image_metadata:
                raise KeyError(f'{image_name} is missing from COLMAP database')

            db_image = image_metadata[image_name]
            camera_frames.setdefault(db_image['camera_id'], frame)

            w2c = np.linalg.inv(c2w)
            q_w2c = [str(v.item()) for v in rotmat2qvec(w2c[:3, :3])]
            t_w2c = [str(v.item()) for v in w2c[:3, -1]]
            line = f"{db_image['image_id']} {' '.join(q_w2c)} {' '.join(t_w2c)} {db_image['camera_id']} {image_name}"
            f.write(line + '\n\n')

    with open(os.path.join(path_prior, 'cameras.txt'), 'w') as f:
        for camera_id, frame in sorted(camera_frames.items()):
            intr = np.array(frame['intrinsics'])
            w, h = frame['width'], frame['height']
            intr4 = [intr[0, 0], intr[1, 1], intr[0, 2], intr[1, 2]]
            intr4 = [str(i.item()) for i in intr4]
            str_intr = ' '.join(intr4)
            f.write(f"{camera_id} PINHOLE {w} {h} {str_intr}" + '\n')

if __name__ == '__main__':
    args = get_opts()

    with open(os.path.join(args.in_path, 'meta_data.json'), 'r') as jf:
        meta_data = json.load(jf)

    path_rigid = os.path.join(args.in_path, 'cam_rigid_config.json')

    auto = COLMAPAuto(args.in_path)

    auto.feature_extract()
    write_prior_model(args, meta_data, auto)
    auto.sequential_matcher()
    auto.point_triangulator()
    if os.path.exists(auto.path_ba):
        shutil.rmtree(auto.path_ba)
    shutil.copytree(auto.path_tri, auto.path_ba)
    auto.rigid_ba(path_rigid)
    auto.point_triangulator_ba()
