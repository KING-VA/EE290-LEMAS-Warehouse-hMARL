import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from utils import init

"""
Modify standard PyTorch distributions so they are compatible with this code.
"""
# Categorical
class FixedCategorical(torch.distributions.Categorical):
    def sample(self):
        return super().sample().unsqueeze(-1)

    def log_probs(self, actions):
        return (
            super()
            .log_prob(actions.squeeze(-1))
            .view(actions.size(0), -1)
            .sum(-1)
            .unsqueeze(-1)
        )

    def mode(self):
        return self.probs.argmax(dim=-1, keepdim=True)


class Categorical(nn.Module):
    def __init__(self, num_inputs, num_outputs):
        super(Categorical, self).__init__()

        init_ = lambda m: init(
            m, nn.init.orthogonal_, lambda x: nn.init.constant_(x, 0), gain=0.01
        )

        self.linear = init_(nn.Linear(num_inputs, num_outputs))

    def forward(self, x, action_mask=None):
        x = self.linear(x)
        if action_mask is not None:
            # Mask logits: set invalid actions to a large negative value
            x = x + (torch.log(action_mask.float() + 1e-8))
        return FixedCategorical(logits=x)
