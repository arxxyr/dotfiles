## note

$HOME/miniconda3/envs/humanoid-gym/etc/conda/activate.d/ld_path.sh

``` bash
#!/bin/sh
# 激活 conda 环境时，将当前环境的 lib 目录添加到 LD_LIBRARY_PATH 中
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

```
 
$HOME/miniconda3/envs/humanoid-gym/etc/conda/deactivate.d/ld_path.sh 
``` bash
#!/bin/sh
# 取消激活 conda 环境时，从 LD_LIBRARY_PATH 中移除当前环境的 lib 目录
if [ -n "$LD_LIBRARY_PATH" ]; then
    export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | sed -e "s|$CONDA_PREFIX/lib:||")
fi

```

pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
pip install numpy==1.23


## useage

train
``` bash
python scripts/train.py --task=humanoid_ppo --run_name v1 --headless --num_envs 4096
```

evaluating
``` bash
python scripts/play.py --task=humanoid_ppo --load_run Feb10_11-25-07_v1  --run_name v1
```

run
``` bash
ython scripts/sim2sim.py --load_model /path/to/logs/XBot_ppo/exported/policies/policy_1.pt
```
