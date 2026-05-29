<a id="readme-top"></a>


adがltfの場合、[こちら](https://huggingface.co/XDimLab/ICCV2025-RealADSim-ClosedLoop-SubmissionDemo/tree/b7857b255a75317adda6ba732337cc3581d3be46/ckpts)をダウンロードし、以下のように配置する。
```bash
NAVSIM_root/ckpts/ltf_seed_0.ckpt
```

---

<!-- PROJECT LOGO -->
<div align="center">
  <img src="assets/hugsim.png" alt="Logo" width="300">
  
  <p>
    <a href="https://xdimlab.github.io/HUGSIM/">
      <img src="https://img.shields.io/badge/Project-Page-green?style=for-the-badge" alt="Project Page" height="20">
    </a>
    <a href="https://arxiv.org/abs/2412.01718">
      <img src="https://img.shields.io/badge/arXiv-Paper-red?style=for-the-badge" alt="arXiv Paper" height="20">
    </a>
  </p>
  
  > Hongyu Zhou<sup>1</sup>, Longzhong Lin<sup>1</sup>, Jiabao Wang<sup>1</sup>, Yichong Lu<sup>1</sup>, Dongfeng Bai<sup>2</sup>, Bingbing Liu<sup>2</sup>, Yue Wang<sup>1</sup>, Andreas Geiger<sup>3,4</sup>, Yiyi Liao<sup>1,†</sup> <br>
  > <sup>1</sup> Zhejiang University <sup>2</sup> Huawei <sup>3</sup> University of Tübingen <sup>4</sup> Tübingen AI Center <br>
  > <sup>†</sup> Corresponding Authors

  <img src="assets/teaser.jpg" width="800" style="display: block; margin: 0 auto;">

  <br>

  <p align="left">
    This is the official project repository of the paper <b>HUGSIM: A Real-Time, Photo-Realistic and Closed-Loop Simulator for Autonomous Driving</b>.
  </p>
  
</div>

---

# Installation

## Development Container

This repository provides a VS Code Dev Container configuration in `.devcontainer/`.
Open this repository with **Dev Containers: Reopen in Container** to build and enter the CUDA 11.8 development environment.

The container is started with host networking, host IPC, privileged device access, X11 socket mounting, and NVIDIA GPU access.
If you use GUI tools from the container, make sure your host allows X11 connections from Docker.

## uv Environment

Run the following commands inside the Docker container or VS Code Dev Container.
If `uv` is not installed in the container yet, install it first:

``` bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

Create the Python 3.11.10 environment and install the HUGSIM dependencies:

``` bash
uv python install 3.11.10
uv sync
```

Verify the environment:

``` bash
uv run python -c "import torch; print(torch.__version__, torch.version.cuda)"
uv run python -c "import hugsim_env"
```

This repository depends on several packages that are built from source against PyTorch and CUDA.
The uv configuration in `pyproject.toml` installs PyTorch from the CUDA 11.8 wheel index and adds the build dependencies required by the CUDA extension packages.

Install apex (required by InverseForm) in the uv environment:

``` bash
uv run --no-sync bash -lc 'cd data/InverseForm && ([ -d apex ] || git clone https://github.com/NVIDIA/apex.git apex) && cd apex && git checkout ac8214ee6ba77c0037c693828e39d83654d25720 && python setup.py install --cuda_ext --cpp_ext'
```

Verify apex:

``` bash
uv run python -c "import apex"
```

Change into the **uv environment** by using the command:

``` bash
source .venv/bin/activate
```

Or you can use `uv run <command>` to run a command in the **uv environment**.


# Data Preparation

Please refer to [Data Preparation Document](data/README.md)

You can download sample data from [here](https://huggingface.co/datasets/hyzhou404/HUGSIM/tree/main/sample_data).

# Reconstruction

``` bash
seq=${seq_name}
input_path=${datadir}/${seq}
output_path=${modeldir}/${seq}
mkdir -p ${output_path}
CUDA_VISIBLE_DEVICES=4 \
python -u train_ground.py --data_cfg ./configs/${dataset_name: [kitti360, waymo, nusc, pandaset]}.yaml \
        --source_path ${input_path} --model_path ${output_path}
CUDA_VISIBLE_DEVICES=4 \
python -u train.py --data_cfg ./configs/${dataset_name}.yaml \
        --source_path ${input_path} --model_path ${output_path}
```

# Scene Export

The reconstructed scene folders contain some information that won't be utilized during the simulation. The scenes are expected to be exported as a minimized format to facilitate easier sharing and simulation.
```bash
 python eval_render/export_scene.py --model_path ${recon_scene_path} --output_path ${export_path} --iteration 30000
``` 
We've made some changes in the capturing and reloading code. If you would like to convert scenes from previous version (before commit 1ca821a8) of our code, add `--ver0` in the above command. 

# Vehicles, Scenes and Scenarios

We have released all 3DRealCar files, along with the complete set of scenes and scenarios, at [release link](https://huggingface.co/datasets/XDimLab/HUGSIM). 
We are also holding a competition at [RealADSim @ ICCV 2025](https://huggingface.co/spaces/XDimLab/ICCV2025-RealADSim-ClosedLoop), so some scenarios and scenarios are hosted privately. We welcome participants to join!

# Scenarios configuration with GUI

**Note that this GUI is only used for configuration scenarios, rather than simulation. The rendering quality in GUI is not the results during simulation**

First convert the vehicles and scenes to splat and semantic format.

``` bash
python eval_render/convert_vehicles.py --vehicle_path ${PATH_3DRealCar}
python eval_render/convert_scene.py --model_path ${PATH_Scene}
```

Then, you can run the GUI to configure the scenario. 
**nuscenes_camera.yaml** in gui/static/data provides a camera configuration template, you can modify it to fit your needs.

``` bash
cd gui
python app.py --scene ${PATH_Scene} --car_folder ${PATH_3DRealCar/converted}
```

You can configure the scenario with the GUI, and download the yaml file to use in simulation.

Here is a video for the GUI usage demonstration: [GUI Video](https://github.com/hyzhou404/HUGSIM/blob/main/assets/hugsim_gui.mp4)

# Simulation

**Before simulation, [UniAD_SIM](https://github.com/hyzhou404/UniAD_SIM), [VAD_SIM](https://github.com/hyzhou404/VAD_SIM) and [NAVSIM](https://github.com/hyzhou404/NAVSIM) client should be installed. The client environments are allowed to be separated from the HUGSIM environment.**

The dependencies for NAVSIM are already specified as the pixi environment file, so you don't need to manually install the dependencies.

In **closed_loop.py**, we automatically launch autonomous driving algorithms.

Paths in **configs/sim/\*\_base.yaml** should be updated as paths on your machine.

``` bash
CUDA_VISIBLE_DEVICES=${sim_cuda} \
python closed_loop.py --scenario_path ./configs/benchmark/${dataset_name}/${scenario_name}.yaml \
            --base_path ./configs/sim/${dataset_name}_base.yaml \
            --camera_path ./configs/sim/${dataset_name}_camera.yaml \
            --kinematic_path ./configs/sim/kinematic.yaml \
            --ad ${method_name: [uniad, vad, ltf]} \
            --ad_cuda ${ad_cuda}
```

Run the following commands to execute.

```bash
sim_cuda=0
ad_cuda=1

# change this variable as the scenario path on your machine
scenario_dir=${SCENARIO_PATH} 

for cfg in ${scenario_dir}/*.yaml; do
    echo ${cfg}
    CUDA_VISIBLE_DEVICES=${sim_cuda} \
    python closed_loop.py --scenario_path ${cfg} \
                        --base_path ./configs/sim/nuscenes_base.yaml \
                        --camera_path ./configs/sim/nuscenes_camera.yaml \
                        --kinematic_path ./configs/sim/kinematic.yaml \
                        --ad uniad \
                        --ad_cuda ${ad_cuda}
done
```

In practice, you may encounter errors due to an incorrect environment, path, and etc. For debugging purposes, you can modify the last part of code as:
```python
# process = launch(ad_path, args.ad_cuda, output)
# try:
#     create_gym_env(cfg, output)
#     check_alive(process)
# except Exception as e:
#     print(e)
#     process.kill()

# For debug
create_gym_env(cfg, output)
```

# TODO list
- [x] Release sample data and results
- [x] Release unicycle model part
- [x] Release GUI
- [x] Release more scenarios

# Citation

If you find our paper and codes useful, please kindly cite us via:

```bibtex
@article{zhou2024hugsim,
  title={HUGSIM: A Real-Time, Photo-Realistic and Closed-Loop Simulator for Autonomous Driving},
  author={Zhou, Hongyu and Lin, Longzhong and Wang, Jiabao and Lu, Yichong and Bai, Dongfeng and Liu, Bingbing and Wang, Yue and Geiger, Andreas and Liao, Yiyi},
  journal={arXiv preprint arXiv:2412.01718},
  year={2024}
}
```
