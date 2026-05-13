#!/bin/bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_root="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${data_root}/.." && pwd)"
cd "${data_root}"

export PYTHONPATH="${PWD}:${repo_root}:${PYTHONPATH:-}"

cuda=0
data="${repo_root}/download/data/nuscenes"
version='interp_12Hz_trainval'
COLMAP_BIN="${COLMAP_BIN:-colmap}"
total_steps=12

log_step() {
        step=$((step + 1))
        printf '\n[%s] step %02d/%02d: %s\n' "${seq}" "${step}" "${total_steps}" "$1"
}

if ! command -v "${COLMAP_BIN}" >/dev/null 2>&1; then
        echo "COLMAP executable not found: ${COLMAP_BIN}" >&2
        echo "Install COLMAP and make sure it is on PATH, or set COLMAP_BIN=/path/to/colmap." >&2
        exit 127
fi

# seq_list=('scene-0411' 'scene-0064' 'scene-0038' 'scene-0013')
seq_list=('scene-1059' )
for seq in "${seq_list[@]}"; do
        echo "==== ${seq} ===="
        step=0
        start=0
        end=180
        out="${repo_root}/download/data/extract_scene/${seq}"

        export CUDA_VISIBLE_DEVICES=$cuda

        log_step "Extract nuScenes frames"
        mkdir -p "${out}"
        python nusc/load.py --datapath "${data}" --version "${version}" --seq "${seq}" --out "${out}" \
                --start "${start}" --end "${end}" --downsample 2 --video

        log_step "Visualize 2D bounding boxes"
        python utils/vis_bbox_2d.py --out "${out}"
        
        # generate semantic mask
        log_step "Generate semantic masks"
        (
                cd InverseForm
                ./infer_nuscenes.sh "${cuda}" "${out}"
        )

        log_step "Create dynamic masks"
        python utils/create_dynamic_mask.py --data_path "${out}" --data_type nuscenes

        # COLMAP sparse model
        log_step "Clean previous COLMAP outputs"
        rm -rf "${out}"/colmap_sparse*
        rm -f "${out}"/database.db*
        rm -rf "${out}/prior"

        log_step "Prepare COLMAP sparse model"
        python nusc/prepare_colmap.py -i "${out}"

        log_step "Convert COLMAP model to PLY"
        "${COLMAP_BIN}" model_converter \
                --input_path "${out}/colmap_sparse_tri" \
                --output_path "${out}/sparse_ba.ply" \
                --output_type PLY

        log_step "Update camera poses"
        python colmap/update_campose.py --datapath "${out}"

        log_step "Visualize updated 2D bounding boxes"
        python utils/vis_bbox_2d.py --out "${out}"

        log_step "Estimate depth"
        python utils/estimate_depth.py --out "${out}"

        log_step "Merge non-ground depth points"
        python utils/merge_depth_wo_ground.py --out "${out}" --total 200000

        log_step "Merge ground depth points"
        python utils/merge_depth_ground.py --out "${out}" --total 200000 --datatype nuscenes

        echo "[${seq}] completed ${total_steps}/${total_steps} steps"
done
