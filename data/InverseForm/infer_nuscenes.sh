#!/bin/bash
set -euo pipefail

cuda=$1
out=$2

export CUDA_VISIBLE_DEVICES=$cuda

model_path=/home/ubuntu/workspace/HUGSIM/download/hrnet48_OCR_HMS_IF_checkpoint.pth
inverseform_ckpt=checkpoints/distance_measures_regressor.pth
edge_args=()

if [ -f "${inverseform_ckpt}" ]; then
    edge_args=(--has_edge True)
else
    echo "Warning: ${inverseform_ckpt} not found. Running inference without InverseForm edge loss." >&2
fi

arr=("FRONT" "FRONT_LEFT" "FRONT_RIGHT" "BACK_LEFT" "BACK_RIGHT" "BACK")
for cam in ${arr[@]}
do
    echo CAM_${cam}
    torchrun --nproc_per_node=1 validation.py \
    --input_dir "${out}/images/CAM_${cam}" \
    --output_dir "${out}/semantics/CAM_${cam}" \
    --model_path "${model_path}" \
    --arch "ocrnet.HRNet_Mscale" --hrnet_base "48" "${edge_args[@]}"
    echo Done
done
