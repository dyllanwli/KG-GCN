import os
import random
import argparse

import torch
import torch.nn as nn
import numpy as np

import net as net
from utils import load_data, load_adj_raw, normalize_adj, sparse_mx_to_torch_sparse_tensor
from sklearn.metrics import f1_score

import dgl
from gnns.gin_net import GINNet_ss
from gnns.gat_net import GATNet_ss
from gnn.net import net as net