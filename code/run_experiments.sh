#!/bin/sh
python train.py backreach --run_name fixT_01 --gym_env PlanarQuad-v0 --seed 2000 --num_iters 40

python train.py backreach --run_name fixT_02 --gym_env PlanarQuad-v0 --seed 3000 --num_iters 40

python train.py backreach --run_name fixT_03 --gym_env PlanarQuad-v0 --seed 4000 --num_iters 40

python train.py ppo_only --run_name ppo_only_01 --gym_env PlanarQuad-v0 --seed 2000 --num_iters 40

python train.py ppo_only --run_name ppo_only_02 --gym_env PlanarQuad-v0 --seed 3000 --num_iters 40

python train.py ppo_only --run_name ppo_only_03 --gym_env PlanarQuad-v0 --seed 4000 --num_iters 40

python train_syz.py backreach --run_name heu_01 --gym_env PlanarQuad-v0 --seed 2000 --num_iters 40 

python train_syz.py backreach --run_name heu_02 --gym_env PlanarQuad-v0 --seed 3000 --num_iters 40 

python train_syz.py backreach --run_name heu_03 --gym_env PlanarQuad-v0 --seed 4000 --num_iters 40 

python train.py backreach --run_name adaptT_01 --gym_env PlanarQuad-v0 --seed 2000 --num_iters 40 --schedule_horizon 

python train.py backreach --run_name adaptT_02 --gym_env PlanarQuad-v0 --seed 3000 --num_iters 40 --schedule_horizon

python train.py backreach --run_name adaptT_03 --gym_env PlanarQuad-v0 --seed 4000 --num_iters 40 --schedule_horizon

