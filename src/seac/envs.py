import os

import gymnasium as gym
import numpy as np
import torch

from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecEnvWrapper


class MADummyVecEnv(DummyVecEnv):
    def __init__(self, env_fns):
        super().__init__(env_fns)
        agents = len(self.observation_space)
        # change this because we want >1 reward
        self.buf_rews = np.zeros((self.num_envs, agents), dtype=np.float32)

def make_env(env_id, seed, rank, wrappers):
    def _thunk():

        env = gym.make(env_id)
        env.reset(seed=seed + rank)

        for wrapper in wrappers:
            env = wrapper(env)
        return env

    return _thunk


def make_vec_envs(
    env_name: str, seed: int, dummy_vecenv: bool, parallel: int, wrappers, device
):
    envs = [
        make_env(env_name, seed, i, wrappers) for i in range(parallel)
    ]

    if dummy_vecenv or len(envs) == 1:
        envs = MADummyVecEnv(envs)
    else:
        envs = SubprocVecEnv(envs, start_method="spawn")

    envs = VecPyTorch(envs, device)
    return envs


class VecPyTorch(VecEnvWrapper):
    def __init__(self, venv, device):
        """Return only every `skip`-th frame"""
        super(VecPyTorch, self).__init__(venv)
        self.device = device
        # TODO: Fix data types

    def reset(self):
        obs = self.venv.reset()
        return [torch.from_numpy(o).to(self.device) for o in obs]
        return obs

    def step_async(self, actions):
        actions = [a.squeeze().cpu().numpy() for a in actions]
        actions = list(zip(*actions))
        return self.venv.step_async(actions)

    def step_wait(self):
        obs, rew, done, info = self.venv.step_wait()
        return (
            [torch.from_numpy(o).float().to(self.device) for o in obs],
            torch.from_numpy(rew).float().to(self.device),
            torch.from_numpy(done).float().to(self.device),
            info,
        )

