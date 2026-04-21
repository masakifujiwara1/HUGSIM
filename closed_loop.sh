#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CUDA_VISIBLE_DEVICES=0 python "${SCRIPT_DIR}/closed_loop.py" --scenario_path "${SCRIPT_DIR}/configs/benchmark/nuscenes/scene-0383-easy-00.yaml" \
    --base_path "${SCRIPT_DIR}/configs/sim/nuscenes_base.yaml" \
    --camera_path "${SCRIPT_DIR}/configs/sim/nuscenes_camera.yaml" \
    --kinematic_path "${SCRIPT_DIR}/configs/sim/kinematic.yaml" \
    --ad ltf \
    --ad_cuda 0
