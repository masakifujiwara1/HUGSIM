#!/bin/bash

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd -- "${script_dir}/../.." && pwd)

export PYTHONPATH="${repo_root}:${PYTHONPATH:-}"

recon_scene_root="${RECON_SCENE_ROOT:-/home/ubuntu/workspace/HUGSIM/download/data/reconstruct_scene}"
export_root="${EXPORT_ROOT:-/home/ubuntu/workspace/HUGSIM/download/data/export_scene}"
iteration="${ITERATION:-30000}"

shopt -s nullglob

found_scene=0
for recon_scene_path in "${recon_scene_root}"/*/; do
        found_scene=1
        seq_name=$(basename "${recon_scene_path%/}")
        export_path="${export_root}/${seq_name}"

        echo "Exporting ${seq_name}"
        mkdir -p "${export_path}"

        python "${repo_root}/eval_render/export_scene.py" \
                --model_path "${recon_scene_path}" \
                --output_path "${export_path}" \
                --iteration "${iteration}"
done

if [ "${found_scene}" -eq 0 ]; then
        echo "No reconstructed scene directories found under ${recon_scene_root}" >&2
        exit 1
fi
