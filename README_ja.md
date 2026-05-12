<a id="readme-top"></a>


ad が ltf の場合、[こちら](https://huggingface.co/XDimLab/ICCV2025-RealADSim-ClosedLoop-SubmissionDemo/tree/b7857b255a75317adda6ba732337cc3581d3be46/ckpts)をダウンロードし、以下のように配置してください。
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
    本リポジトリは、論文 <b>HUGSIM: A Real-Time, Photo-Realistic and Closed-Loop Simulator for Autonomous Driving</b> の公式プロジェクトリポジトリです。
  </p>
  
</div>

---

# インストール

## 開発コンテナ

このリポジトリには、`.devcontainer/` に VS Code Dev Container の設定が含まれています。
VS Code の **Dev Containers: Reopen in Container** でこのリポジトリを開くと、CUDA 11.8 の開発環境をビルドして入ることができます。

コンテナは、ホストネットワーク、ホスト IPC、privileged デバイスアクセス、X11 ソケットマウント、NVIDIA GPU アクセスを有効にして起動します。
コンテナ内から GUI ツールを使う場合は、ホスト側で Docker からの X11 接続を許可してください。

## uv 環境

以下のコマンドは Docker コンテナ、または VS Code Dev Container の中で実行してください。
コンテナに `uv` がまだインストールされていない場合は、先にインストールします。

``` bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

Python 3.11.10 環境を作成し、HUGSIM の依存関係をインストールします。

``` bash
uv python install 3.11.10
uv sync
```

環境を確認します。

``` bash
uv run python -c "import torch; print(torch.__version__, torch.version.cuda)"
uv run python -c "import hugsim_env"
```

このリポジトリはいくつかのソースビルドが必要なパッケージに依存しており、それらは PyTorch と CUDA に対してビルドされます。
`pyproject.toml` の uv 設定では、CUDA 11.8 の wheel index から PyTorch をインストールし、CUDA extension パッケージのビルドに必要な build dependency を追加します。

InverseForm に必要な apex を uv 環境にインストールします。

``` bash
uv run --no-sync bash -lc 'cd data/InverseForm && ([ -d apex ] || git clone https://github.com/NVIDIA/apex.git apex) && cd apex && git checkout ac8214ee6ba77c0037c693828e39d83654d25720 && python setup.py install --cuda_ext --cpp_ext'
```

apex を確認します。

``` bash
uv run python -c "import apex"
```

**uv 環境**に入るには、次のコマンドを使います。

``` bash
source .venv/bin/activate
```

また、`uv run <command>` を使うことで、**uv 環境**内でコマンドを実行できます。


# データ準備

[Data Preparation Document](data/README.md) を参照してください。

サンプルデータは[こちら](https://huggingface.co/datasets/hyzhou404/HUGSIM/tree/main/sample_data)からダウンロードできます。

# 再構成

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

# シーンのエクスポート

再構成されたシーンフォルダには、シミュレーション中には使用されない情報も含まれています。共有やシミュレーションをしやすくするため、シーンは最小化された形式でエクスポートすることを想定しています。
```bash
 python eval_render/export_scene.py --model_path ${recon_scene_path} --output_path ${export_path} --iteration 30000
``` 
キャプチャおよび再読み込みのコードにはいくつか変更が加えられています。以前のバージョン、具体的には commit `1ca821a8` より前のコードで作成したシーンを変換したい場合は、上記コマンドに `--ver0` を追加してください。

# 車両、シーン、シナリオ

すべての 3DRealCar ファイル、シーン一式、シナリオ一式を[リリースリンク](https://huggingface.co/datasets/XDimLab/HUGSIM)で公開しています。
また、[RealADSim @ ICCV 2025](https://huggingface.co/spaces/XDimLab/ICCV2025-RealADSim-ClosedLoop) というコンペティションも開催しているため、一部のシナリオは非公開でホストされています。参加を歓迎します。

# GUI によるシナリオ設定

**この GUI はシミュレーションではなく、シナリオ設定のためだけに使用します。GUI 上のレンダリング品質は、シミュレーション中の結果とは異なります。**

まず、車両とシーンを splat 形式および semantic 形式に変換します。

``` bash
python eval_render/convert_vehicles.py --vehicle_path ${PATH_3DRealCar}
python eval_render/convert_scene.py --model_path ${PATH_Scene}
```

その後、GUI を起動してシナリオを設定できます。
`gui/static/data` 内の **nuscenes_camera.yaml** はカメラ設定のテンプレートです。必要に応じて変更してください。

``` bash
cd gui
python app.py --scene ${PATH_Scene} --car_folder ${PATH_3DRealCar/converted}
```

GUI でシナリオを設定し、シミュレーションで使用する yaml ファイルをダウンロードできます。

GUI の使用方法を示す動画はこちらです: [GUI Video](https://github.com/hyzhou404/HUGSIM/blob/main/assets/hugsim_gui.mp4)

# シミュレーション

**シミュレーションの前に、[UniAD_SIM](https://github.com/hyzhou404/UniAD_SIM)、[VAD_SIM](https://github.com/hyzhou404/VAD_SIM)、[NAVSIM](https://github.com/hyzhou404/NAVSIM) のクライアントをインストールしておく必要があります。これらのクライアント環境は HUGSIM 環境とは分けてもかまいません。**

NAVSIM の依存関係は Pixi 環境ファイルとしてすでに定義されているため、手動で依存関係をインストールする必要はありません。

**closed_loop.py** では、自動運転アルゴリズムを自動的に起動します。

**configs/sim/\*\_base.yaml** 内のパスは、自分のマシン上のパスに更新してください。

``` bash
CUDA_VISIBLE_DEVICES=${sim_cuda} \
python closed_loop.py --scenario_path ./configs/benchmark/${dataset_name}/${scenario_name}.yaml \
            --base_path ./configs/sim/${dataset_name}_base.yaml \
            --camera_path ./configs/sim/${dataset_name}_camera.yaml \
            --kinematic_path ./configs/sim/kinematic.yaml \
            --ad ${method_name: [uniad, vad, ltf]} \
            --ad_cuda ${ad_cuda}
```

実行するには、次のコマンドを使います。

```bash
sim_cuda=0
ad_cuda=1

# この変数を自分のマシン上のシナリオパスに変更してください
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

実際には、環境やパスなどが正しくないことでエラーが発生する場合があります。デバッグのため、コード末尾を次のように変更できます。
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

# TODO リスト
- [x] サンプルデータと結果を公開
- [x] unicycle model 部分を公開
- [x] GUI を公開
- [x] 追加シナリオを公開

# 引用

本論文およびコードが役に立った場合は、以下の形式で引用してください。

```bibtex
@article{zhou2024hugsim,
  title={HUGSIM: A Real-Time, Photo-Realistic and Closed-Loop Simulator for Autonomous Driving},
  author={Zhou, Hongyu and Lin, Longzhong and Wang, Jiabao and Lu, Yichong and Bai, Dongfeng and Liu, Bingbing and Wang, Yue and Geiger, Andreas and Liao, Yiyi},
  journal={arXiv preprint arXiv:2412.01718},
  year={2024}
}
```
