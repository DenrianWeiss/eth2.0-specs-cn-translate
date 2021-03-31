# 以太坊 2.0 规范

[![Join the chat at https://discord.gg/qGpsxSA](https://img.shields.io/badge/chat-on%20discord-blue.svg)](https://discord.gg/qGpsxSA) [![Join the chat at https://gitter.im/ethereum/sharding](https://badges.gitter.im/ethereum/sharding.svg)](https://gitter.im/ethereum/sharding?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

如欲更深入了解分片链和以太坊2.0,请参阅 [分片链问答（英文）](https://eth.wiki/sharding/Sharding-FAQs) 和 [研究摘要（英文）](https://notes.ethereum.org/s/H1PGqDhpm).

本仓库存有当前的 Eth2 规范。对于设计理念或者改进建议的想法可以在 issue 中提出并讨论。而对本规范已经达成共识并成型的变更可以通过 pull request 进行。

## 翻译说明

（本节为翻译版本特有的内容）
本翻译版本仅为便于查阅提供，译者不对翻译准确性负责，亦不对内容的及时性作出任何保证，而对于规范的讨论应于原仓库中作出，本仓库的 issue 等功能仅作为管理翻译版本的一种方式存在，望周知。
另注：为保持内容不变性，原文中的链接等皆保持原状，而不做进一步处理。而论文等引用内容标题则视情况判断翻译与否。

## 规范

[![GitHub release](https://img.shields.io/github/v/release/ethereum/eth2.0-specs)](https://github.com/ethereum/eth2.0-specs/releases/) [![PyPI version](https://badge.fury.io/py/eth2spec.svg)](https://badge.fury.io/py/eth2spec)

Eth2 客户端的核心规范已按照功能分门别类放入[specs](specs/)文件夹中。其功能特性将被同时研究开发，并在完成后整理成一系列的更新。

目前的功能阶段如下：

### 第 0 阶段（创世阶段）

* [信标链](specs/phase0/beacon-chain.md)
* [信标链分叉选择](specs/phase0/fork-choice.md)
* [信标链预存合约](specs/phase0/deposit-contract.md)
* [诚实验证者](specs/phase0/validator.md)
* [点对点网络](specs/phase0/p2p-interface.md)

### 牵牛星(Altair)分叉

* [信标链变化](specs/altair/beacon-chain.md)
* [牵牛星分叉](specs/altair/fork.md)
* [轻量客户端同步协议](specs/altair/sync-protocol.md)
* [诚实验证者准则变更](specs/altair/validator.md)

### 主链合并

合并阶段仍然在频繁的研发之中。因此，本规范仅对工程工作作出一个方向性的指导，而技术细节仍在评审之中，并可能存在将来的变更。

* 背景材料l:
  * 一篇 [ethresear.ch](https://ethresear.ch) 帖子 [描述了合并的基本机制](https://ethresear.ch/t/the-eth1-eth2-transition/6265)
  * [ethereum.org](https://ethereum.org) 上对合并的从更高层次上的 [描述](https://ethereum.org/en/eth2/docking/)
* Specifications:
  * [信标链变更](specs/merge/beacon-chain.md)
  * [分叉选择变更](specs/merge/fork-choice.md)
  * [验证者的额外要求](specs/merge/validator.md)

### 分片

分片阶段在以太坊一二代合并之后，被划分为了如下三个阶段：

* 分片基本功能 - 仍在研发阶段早期
  * [信标链变更](specs/sharding/beacon-chain.md)
  * [点对点网络变更](specs/sharding/p2p-interface.md)
* 托管博弈 - 已完成，基于分片规范 
  * [信标链变更](specs/custody_game/beacon-chain.md)
  * [验证者的托管工作](specs/custody_game/validator.md)
* 数据有效性取样 - 仍在研发当中
  * 技术细节 [here](https://hackmd.io/@HWeNw8hNRimMm2m2GH56Cw/B1YJPGkpD).
  * [核心类型和函数](specs/das/das-core.md)
  * [点对点网络](specs/das/p2p-interface.md)
  * [分支选择](specs/das/fork-choice.md)
  * [取样过程](specs/das/sampling.md)

### [规范](specs) 中包括的附加文件包括:

* [简易序列化 (SSZ) 规范](ssz/simple-serialize.md)
* [Merkle 证明格式](ssz/merkle-proofs.md)
* [一般验证格式规范](tests/formats/README.md)

## 适用于客户端实现的额外规范

除客户端必须实现的功能之外的标准和规范刻在如下仓库中找到：

* [Eth2 APIs](https://github.com/ethereum/eth2.0-apis)
* [Eth2 遥测指标](https://github.com/ethereum/eth2.0-metrics/)
* [Eth2 项目管理的互操作性要求](https://github.com/ethereum/eth2.0-pm/tree/master/interop)

## 设计目标

下面是 以太坊 2.0 的总体设计目标:
* 降低复杂性，即使会损失一部分效率
* 在大部分网络和很大一部分节点离线时仍保持可用性
* 保证所有组件对于量子计算安全，或者能够轻易的在量子安全的组件可用时被换掉
* 使用允许在长期和短期内与必须尽可能多的验证者参与验证的密码学和设计技巧
* 允许具有 `O(C)` 等级资源的消费级笔记本能够在 `O(1)` 时间内处理或验证分片链（这应当包括任何系统等级的验证，包括信标链）

## Useful external resources

* [设计原则](https://notes.ethereum.org/s/rkhCgQteN#)
* [创世阶段的参与教程](https://notes.ethereum.org/s/Bkn3zpwxB)
* [Combining GHOST and Casper paper](https://arxiv.org/abs/2003.03052)

## 对规范贡献者可能有用的资源

在规范编写过程中使用的不同组建的文档在这里：
* [YAML 测试生成器](tests/generators/README.md)
* [带有 Py-test 的可执行的 Python 规范](tests/core/pyspec/README.md)
