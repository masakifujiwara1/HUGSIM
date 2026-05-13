#!/bin/bash

set -euo pipefail

export PYTHONPATH="${PWD}:${PYTHONPATH:-}"

cuda=0
datadir='/home/ubuntu/workspace/HUGSIM/download/data/extract_scene'
modeldir='/home/ubuntu/workspace/HUGSIM/download/data/reconstruct_scene'
dataset_name='nusc'

shopt -s nullglob

print_preprocess_hint() {
        local input_path=$1

        echo "Run the preprocessing commands before reconstruction:" >&2
        echo "  (cd data/InverseForm && ./infer_nuscenes.sh ${cuda} ${input_path%/})" >&2
        echo "  python data/utils/create_dynamic_mask.py --data_path ${input_path%/} --data_type nuscenes" >&2
        echo "  python data/utils/estimate_depth.py --out ${input_path%/}" >&2
        echo "  python data/utils/merge_depth_wo_ground.py --out ${input_path%/} --total 200000" >&2
        echo "  python data/utils/merge_depth_ground.py --out ${input_path%/} --total 200000 --datatype nuscenes" >&2
}

check_required_file() {
        local input_path=$1
        local file_name=$2

        if [ ! -f "${input_path}/${file_name}" ]; then
                echo "Missing ${input_path}/${file_name}" >&2
                print_preprocess_hint "${input_path}"
                exit 1
        fi
}

found_seq=0
for input_path in "${datadir}"/*/; do
        found_seq=1
        seq_name=$(basename "${input_path%/}")
        output_path="${modeldir}/${seq_name}"

        echo "${seq_name}"
        check_required_file "${input_path}" "points3d.ply"
        check_required_file "${input_path}" "ground_points3d.ply"
        check_required_file "${input_path}" "ground_param.pkl"

        mkdir -p "${output_path}"
        CUDA_VISIBLE_DEVICES=${cuda} \
        python -u train_ground.py --data_cfg ./configs/${dataset_name}.yaml \
                --source_path "${input_path}" --model_path "${output_path}"

        ground_ckpt="${output_path}/ckpts/ground_chkpnt30000.pth"
        if [ ! -f "${ground_ckpt}" ]; then
                echo "Missing ${ground_ckpt}" >&2
                echo "train.py expects this checkpoint from train_ground.py." >&2
                exit 1
        fi

        CUDA_VISIBLE_DEVICES=${cuda} \
        python -u train.py --data_cfg ./configs/${dataset_name}.yaml \
                --source_path "${input_path}" --model_path "${output_path}"
done

if [ "${found_seq}" -eq 0 ]; then
        echo "No sequence directories found under ${datadir}" >&2
        exit 1
fi
