import os
import random
import argparse

import torch
import torch.nn as nn
import numpy as np

from utils import load_data, load_adj_raw, normalize_adj, sparse_mx_to_torch_sparse_tensor
from sklearn.metrics import f1_score

# import dgl
from gcn.net import net_gcn, net_gcn_multitask

import wandb


def run(args, seed):
    setup_seed(seed)
    adj, features, labels, idx_train, idx_val, idx_test = load_data(args['dataset'])

    node_num = features.size()[0]
    class_num = labels.numpy().max() + 1

    adj = adj.cuda()
    features = features.cuda()
    labels = labels.cuda()

    loss_func = nn.CrossEntropyLoss()
    loss_func_ss = nn.L1Loss()
    early_stopping = 10

    adj_raw = load_adj_raw(args['dataset']).tocsr()
    idx_mask = list(range(node_num))
    adj_mask = adj_raw
    adj_mask[idx_mask, idx_mask] = 0
    adj_mask = sparse_mx_to_torch_sparse_tensor(normalize_adj(adj_mask)).cuda()

    reduced_dim = args['reduced_dimension']
    ss_labels, _, _ = features.svd()
    ss_labels = ss_labels[:, :reduced_dim].cuda()

    # get gcn
    net_gcn = net_gcn_multitask(embedding_dim=args['embedding_dim'], ss_dim=args['reduced_dimension'])
    net_gcn = net_gcn.cuda()
    optimizer = torch.optim.Adam(net_gcn.parameters(), lr=args['lr'], weight_decay=args['weight_decay'])
    best_val = 0
    best_val_test = 0
    for epoch in range(500):

        optimizer.zero_grad()
        output, _ = net_gcn(features, adj)
        _, output_ss = net_gcn(features, adj_mask)
        loss_target = loss_func(output[idx_train], labels[idx_train])
        loss_ss = loss_func_ss(output_ss, ss_labels) * 1e2
        loss = loss_target + loss_ss * args['loss_weight']
        wandb.log({
            "epoch": epoch,
            "loss": loss_target.data
        })
        # print('epoch', epoch, 'loss', loss_target.data)
        loss.backward()
        optimizer.step()

        # validation
        with torch.no_grad():
            output, _ = net_gcn(features, adj, val_test=True)
            # loss_val.append(loss_func(output[idx_val], labels[idx_val]).cpu().numpy())
            wandb.log({
                'val_acc': f1_score(labels[idx_val].cpu().numpy(), output[idx_val].cpu().numpy().argmax(axis=1), average='micro')
            })
            # print('val acc', f1_score(labels[idx_val].cpu().numpy(), output[idx_val].cpu().numpy().argmax(axis=1), average='micro'))

            acc_val = f1_score(labels[idx_val].cpu().numpy(), output[idx_val].cpu().numpy().argmax(axis=1), average='micro')
            acc_test = f1_score(labels[idx_test].cpu().numpy(), output[idx_test].cpu().numpy().argmax(axis=1), average='micro')
            if acc_val > best_val:
                best_val = acc_val
                best_val_test = acc_test

    return best_val, best_val_test


def parser_loader():
    parser = argparse.ArgumentParser(description='Self-Supervised GCN')
    parser.add_argument('--dataset', type=str, default='cora')
    parser.add_argument('--embedding-dim', nargs='+', type=int, default=[1433,16,7])
    parser.add_argument('--lr', type=float, default=0.08)
    parser.add_argument('--weight-decay', type=float, default=8e-4)
    parser.add_argument('--reduced-dimension', type=int, default=48)
    parser.add_argument('--loss-weight', type=float, default=0.3)
    parser.add_argument('--grid-search', type=bool, default=False)
    return parser


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    np.random.seed(seed)
    random.seed(seed)


if __name__ == "__main__":

    wandb.init(project="ssgcn")
    # os.environ['CUDA_VISIBLE_DEVICES'] = '0'

    parser = parser_loader()
    args = vars(parser.parse_args(""))
    print("args", args)

    if not args['grid_search']:

        acc_val = np.zeros(50)
        acc_test = np.zeros(50)
        for seed in range(50):
            # run code
            print("starting")
            acc_val[seed], acc_test[seed] = run(args, seed)
            print('seed', seed, 'val', acc_val[seed], 'test', acc_test[seed])

        print('finish')
        print('val mean', acc_val.mean(), 'val std', acc_val.std())
        print('test mean', acc_test.mean(), 'test std', acc_test.std())

    else:

        pn_list = [24, 28, 32, 36, 40, 44, 48]
        lw_list = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        pn_len = len(pn_list)
        lw_len = len(lw_list)
        acc_val_table = np.zeros((pn_len, lw_len))

        for i in range(pn_len):
            for j in range(lw_len):

                args['reduced_dimension'] = pn_list[i]
                args['loss_weight'] = lw_list[j]

                acc_val = np.zeros(10)
                for seed in range(10):
                    acc_val[seed], _ = run(args, seed)
                acc_val_table[i, j] = acc_val.mean()

        print('finish')
        print('val mean table', acc_val_table)