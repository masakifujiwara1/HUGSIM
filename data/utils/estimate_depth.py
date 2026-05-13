import argparse
import glob
import os
import json
import numpy as np
import torch
from tqdm import tqdm
from unidepth.models import UniDepthV2
from PIL import Image


def disable_unusable_xformers():
    """Fall back to PyTorch SDPA when xFormers was installed for another CUDA."""
    try:
        from unidepth.models.backbones.metadinov2 import attention, block
    except ImportError:
        return

    if not getattr(attention, "XFORMERS_AVAILABLE", False):
        return

    if not torch.cuda.is_available():
        attention.XFORMERS_AVAILABLE = False
        block.XFORMERS_AVAILABLE = False
        return

    try:
        q = torch.empty((1, 1, 1, 16), device="cuda", dtype=torch.float16)
        attention.memory_efficient_attention(q, q, q)
    except Exception as exc:
        attention.XFORMERS_AVAILABLE = False
        block.XFORMERS_AVAILABLE = False
        print(
            "xFormers CUDA attention is unavailable; "
            f"falling back to PyTorch SDPA ({exc.__class__.__name__})."
        )


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, required=True)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_opts()
    
    disable_unusable_xformers()

    print('loading depth model...')
    model = UniDepthV2.from_pretrained("lpiccinelli/unidepth-v2-vitl14", force_download=True)
    model = model.to("cuda")
    model.eval()
    print("Depth model loaded")
    
    os.makedirs(os.path.join(args.out, 'depth'), exist_ok=True)
    for cam_pth in glob.glob(os.path.join(args.out, 'images', '*')):
        cam = os.path.basename(cam_pth)
        os.makedirs(os.path.join(args.out, 'depth', cam), exist_ok=True)
    
    with open(os.path.join(args.out, 'meta_data.json')) as f:
        meta_data = json.load(f)
    
    for frame in tqdm(meta_data['frames']):
        im_path = os.path.join(args.out, frame['rgb_path'])
        K = np.array(frame['intrinsics'])
        K = torch.from_numpy(K[:3, :3]).float().cuda()
        image = torch.from_numpy(np.array(Image.open(im_path))).permute(2, 0, 1)
        prediction = model.infer(image, K)
        depth = prediction["depth"][0][0].detach().cpu()  # Depth in [m].
        
        depth_path = os.path.join(
            args.out,
            im_path.replace("images", "depth")
            .replace("./", "")
            .replace(".jpg", ".pt")
            .replace(".png", ".pt"),
        )
        
        torch.save(depth, depth_path)
