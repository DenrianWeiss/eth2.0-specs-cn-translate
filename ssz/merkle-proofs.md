# Merkle 证明格式

**注意**: 本文档对于设计者和实现者仍处于施工当中。

## 目录
<!-- TOC -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [辅助函数](#%E8%BE%85%E5%8A%A9%E5%87%BD%E6%95%B0)
- [Merkle 树的整体下标](#merkle-%E6%A0%91%E7%9A%84%E6%95%B4%E4%BD%93%E4%B8%8B%E6%A0%87)
- [索引简单序列化（SSZ）对象](#%E7%B4%A2%E5%BC%95%E7%AE%80%E5%8D%95%E5%BA%8F%E5%88%97%E5%8C%96ssz%E5%AF%B9%E8%B1%A1)
  - [Helpers for generalized indices](#helpers-for-generalized-indices)
    - [`concat_generalized_indices`](#concat_generalized_indices)
    - [`get_generalized_index_length`](#get_generalized_index_length)
    - [`get_generalized_index_bit`](#get_generalized_index_bit)
    - [`generalized_index_sibling`](#generalized_index_sibling)
    - [`generalized_index_child`](#generalized_index_child)
    - [`generalized_index_parent`](#generalized_index_parent)
- [Merkle multiproofs](#merkle-multiproofs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<!-- /TOC -->

## 辅助函数

```python
def get_power_of_two_ceil(x: int) -> int:
    """
    返回最接近且大于输入的数的2的自然数幂。
    Commonly used for "how many nodes do I need for a bottom tree layer fitting x elements?"
    Example: 0->1, 1->1, 2->2, 3->4, 4->4, 5->8, 6->8, 7->8, 8->8, 9->16.
    """
    if x <= 1:
        return 1
    elif x == 2:
        return 2
    else:
        return 2 * get_power_of_two_ceil((x + 1) // 2)
```

```python
def get_power_of_two_floor(x: int) -> int:
    """
    返回最接近且大于输入的数的2的自然数幂。
    The zero case is a placeholder and not used for math with generalized indices.
    Commonly used for "what power of two makes up the root bit of the generalized index?"
    Example: 0->1, 1->1, 2->2, 3->2, 4->4, 5->4, 6->4, 7->4, 8->8, 9->8
    """
    if x <= 1:
        return 1
    if x == 2:
        return x
    else:
        return 2 * get_power_of_two_floor(x // 2)
```

## Merkle 树的整体下标

在二叉 Merkle 树中, 我们定义一个节点的 "整体下标" 为 `2**depth + index`. 用图表达则如下图:

```
    1
 2     3
4 5   6 7
   ...
```

我们能够注意到整体下标有一个好的性质，也就是一个节点 `k` 的子节点的整体下标是 `2k` 和 `2k+1`, 而且还等于节点在以如下函数计算出的 Merkle 树线性表示中的位置

```python
def merkle_tree(leaves: Sequence[Bytes32]) -> Sequence[Bytes32]:
    """
    返回 Merkle 树中的节点按整体下标排列后的数组: 
    [0, 1, 2, 3, 4, 5, 6, 7], 在其中 0 应当被忽略，而 1 为树根。结果将是填充后的输入的树叶的最底层节点的两倍大小。
    """
    bottom_length = get_power_of_two_ceil(len(leaves))
    o = [Bytes32()] * bottom_length + list(leaves) + [Bytes32()] * (bottom_length - len(leaves))
    for i in range(bottom_length - 1, 0, -1):
        o[i] = hash(o[i * 2] + o[i * 2 + 1])
    return o
```

我们在本文档中将 `GeneralizedIndex` 这一自定义类型定义为 Python 中的整数。它也可以以 Bitvector/Bitlist 对象表现。

我们将用总体下标定义 Merkle 证明。

## 索引简单序列化（SSZ）对象

我们可以将任何以 `hash_tree_root(object)` 为树根的简单序列化对象的哈希树表现为不同高度的二分 Merkle 树。
例如，一个 `{x: bytes32, y: List[uint64]}` 对象将会表现成下面这样：

```
     root
    /    \
   x    y_root
        /    \
y_data_root  len(y)
    / \
   /\ /\
  .......
```

现在我们可以定义“path“的概念。”path“是一种描述一个接收一个简单序列化对象并输出一个（可能在很深层次的）特定对象的函数。 
例如， `foo -> foo.x` 是 path，就像`foo -> len(foo.y)` 和 `foo -> foo.y[5].w`一样。这里我们将以列表形式表示path。而它有两种不同形式。在人类可读形式中，它们分别对应： `["x"]`， `["y", "__len__"]` 和 `["y", 5, "w"]` 。而在编码形式中，它们以 `uint64` 类别的值的列表形式表示。在这些情况下（假设`foo` 的成员按 `x`, `y` 的顺序排列，而且 `w` 是 `y[i]` 的第一个属性） `[0]`, `[1, 2**64-1]`, `[1, 5, 0]`. 我们定义 `SSZVariableName` 为成员变量的属性名，那么一个 path 可以表达成整数数组和 `SSZVariableName` 的数组.

```python
def item_length(typ: SSZType) -> int:
    """
    对于简单类型返回它的大小，而复杂类型则是32（一个完整哈希的大小）
    """
    if issubclass(typ, BasicValue):
        return typ.byte_len
    else:
        return 32
```

```python
def get_elem_type(typ: Union[BaseBytes, BaseList, Container],
                  index_or_variable_name: Union[int, SSZVariableName]) -> SSZType:
    """
    返回一个对象在指定索引或成员变量名位置的对象的类型。
    (eg. `7` for `x[7]`, `"foo"` for `x.foo`)
    """
    return typ.get_fields()[index_or_variable_name] if issubclass(typ, Container) else typ.elem_type
```

```python
def chunk_count(typ: SSZType) -> int:
    """
    返回表达指定类型的顶层元素所需的哈希值数量。
    (eg. `x.foo` or `x[7]` but not `x[7].bar` or `x.foo.baz`). 在除了基本类型的数组之外的情况下，因为一个对象对应一个哈希，哈希数量就是顶层元素的数量。
    对于基本类型的数组，一般来说会更少，因为多个基本类型元素可以被打包到一个32字节的块内。
    """
    # typ.length describes the limit for list types, or the length for vector types.
    if issubclass(typ, BasicValue):
        return 1
    elif issubclass(typ, Bits):
        return (typ.length + 255) // 256
    elif issubclass(typ, Elements):
        return (typ.length * item_length(typ.elem_type) + 31) // 32
    elif issubclass(typ, Container):
        return len(typ.get_fields())
    else:
        raise Exception(f"Type not supported: {typ}")
```

```python
def get_item_position(typ: SSZType, index_or_variable_name: Union[int, SSZVariableName]) -> Tuple[int, int, int]:
    """
    Return three variables:
        (i) the index of the chunk in which the given element of the item is represented;
        (ii) the starting byte position within the chunk;
        (iii) the ending byte position within the chunk.
    For example: for a 6-item list of uint64 values, index=2 will return (0, 16, 24), index=5 will return (1, 8, 16)
    """
    if issubclass(typ, Elements):
        index = int(index_or_variable_name)
        start = index * item_length(typ.elem_type)
        return start // 32, start % 32, start % 32 + item_length(typ.elem_type)
    elif issubclass(typ, Container):
        variable_name = index_or_variable_name
        return typ.get_field_names().index(variable_name), 0, item_length(get_elem_type(typ, variable_name))
    else:
        raise Exception("Only lists/vectors/containers supported")
```

```python
def get_generalized_index(typ: SSZType, path: Sequence[Union[int, SSZVariableName]]) -> GeneralizedIndex:
    """
    Converts a path (eg. `[7, "foo", 3]` for `x[7].foo[3]`, `[12, "bar", "__len__"]` for
    `len(x[12].bar)`) into the generalized index representing its position in the Merkle tree.
    """
    root = GeneralizedIndex(1)
    for p in path:
        assert not issubclass(typ, BasicValue)  # If we descend to a basic type, the path cannot continue further
        if p == '__len__':
            typ = uint64
            assert issubclass(typ, (List, ByteList))
            root = GeneralizedIndex(root * 2 + 1)
        else:
            pos, _, _ = get_item_position(typ, p)
            base_index = (GeneralizedIndex(2) if issubclass(typ, (List, ByteList)) else GeneralizedIndex(1))
            root = GeneralizedIndex(root * base_index * get_power_of_two_ceil(chunk_count(typ)) + pos)
            typ = get_elem_type(typ, p)
    return root
```

### Helpers for generalized indices

_Usage note: functions outside this section should manipulate generalized indices using only functions inside this section. This is to make it easier for developers to implement generalized indices with underlying representations other than bigints._

#### `concat_generalized_indices`

```python
def concat_generalized_indices(*indices: GeneralizedIndex) -> GeneralizedIndex:
    """
    Given generalized indices i1 for A -> B, i2 for B -> C .... i_n for Y -> Z, returns
    the generalized index for A -> Z.
    """
    o = GeneralizedIndex(1)
    for i in indices:
        o = GeneralizedIndex(o * get_power_of_two_floor(i) + (i - get_power_of_two_floor(i)))
    return o
```

#### `get_generalized_index_length`

```python
def get_generalized_index_length(index: GeneralizedIndex) -> int:
    """
    Return the length of a path represented by a generalized index.
    """
    return int(log2(index))
```

#### `get_generalized_index_bit`

```python
def get_generalized_index_bit(index: GeneralizedIndex, position: int) -> bool:
    """
    Return the given bit of a generalized index.
    """
    return (index & (1 << position)) > 0
```

#### `generalized_index_sibling`

```python
def generalized_index_sibling(index: GeneralizedIndex) -> GeneralizedIndex:
    return GeneralizedIndex(index ^ 1)
```

#### `generalized_index_child`

```python
def generalized_index_child(index: GeneralizedIndex, right_side: bool) -> GeneralizedIndex:
    return GeneralizedIndex(index * 2 + right_side)
```

#### `generalized_index_parent`

```python
def generalized_index_parent(index: GeneralizedIndex) -> GeneralizedIndex:
    return GeneralizedIndex(index // 2)
```

## Merkle multiproofs

We define a Merkle multiproof as a minimal subset of nodes in a Merkle tree needed to fully authenticate that a set of nodes actually are part of a Merkle tree with some specified root, at a particular set of generalized indices. For example, here is the Merkle multiproof for positions 0, 1, 6 in an 8-node Merkle tree (i.e. generalized indices 8, 9, 14):

```
       .
   .       .
 .   *   *   .
x x . . . . x *
```

. are unused nodes, * are used nodes, x are the values we are trying to prove. Notice how despite being a multiproof for 3 values, it requires only 3 auxiliary nodes, only one node more than would be required to prove a single value. Normally the efficiency gains are not quite that extreme, but the savings relative to individual Merkle proofs are still significant. As a rule of thumb, a multiproof for k nodes at the same level of an n-node tree has size `k * (n/k + log(n/k))`.

First, we provide a method for computing the generalized indices of the auxiliary tree nodes that a proof of a given set of generalized indices will require:

```python
def get_branch_indices(tree_index: GeneralizedIndex) -> Sequence[GeneralizedIndex]:
    """
    Get the generalized indices of the sister chunks along the path from the chunk with the
    given tree index to the root.
    """
    o = [generalized_index_sibling(tree_index)]
    while o[-1] > 1:
        o.append(generalized_index_sibling(generalized_index_parent(o[-1])))
    return o[:-1]
```

```python
def get_path_indices(tree_index: GeneralizedIndex) -> Sequence[GeneralizedIndex]:
    """
    Get the generalized indices of the chunks along the path from the chunk with the
    given tree index to the root.
    """
    o = [tree_index]
    while o[-1] > 1:
        o.append(generalized_index_parent(o[-1]))
    return o[:-1]
```

```python
def get_helper_indices(indices: Sequence[GeneralizedIndex]) -> Sequence[GeneralizedIndex]:
    """
    Get the generalized indices of all "extra" chunks in the tree needed to prove the chunks with the given
    generalized indices. Note that the decreasing order is chosen deliberately to ensure equivalence to the
    order of hashes in a regular single-item Merkle proof in the single-item case.
    """
    all_helper_indices: Set[GeneralizedIndex] = set()
    all_path_indices: Set[GeneralizedIndex] = set()
    for index in indices:
        all_helper_indices = all_helper_indices.union(set(get_branch_indices(index)))
        all_path_indices = all_path_indices.union(set(get_path_indices(index)))

    return sorted(all_helper_indices.difference(all_path_indices), reverse=True)
```

Now we provide the Merkle proof verification functions. First, for single item proofs:

```python
def calculate_merkle_root(leaf: Bytes32, proof: Sequence[Bytes32], index: GeneralizedIndex) -> Root:
    assert len(proof) == get_generalized_index_length(index)
    for i, h in enumerate(proof):
        if get_generalized_index_bit(index, i):
            leaf = hash(h + leaf)
        else:
            leaf = hash(leaf + h)
    return leaf
```

```python
def verify_merkle_proof(leaf: Bytes32, proof: Sequence[Bytes32], index: GeneralizedIndex, root: Root) -> bool:
    return calculate_merkle_root(leaf, proof, index) == root
```

Now for multi-item proofs:

```python
def calculate_multi_merkle_root(leaves: Sequence[Bytes32],
                                proof: Sequence[Bytes32],
                                indices: Sequence[GeneralizedIndex]) -> Root:
    assert len(leaves) == len(indices)
    helper_indices = get_helper_indices(indices)
    assert len(proof) == len(helper_indices)
    objects = {
        **{index: node for index, node in zip(indices, leaves)},
        **{index: node for index, node in zip(helper_indices, proof)}
    }
    keys = sorted(objects.keys(), reverse=True)
    pos = 0
    while pos < len(keys):
        k = keys[pos]
        if k in objects and k ^ 1 in objects and k // 2 not in objects:
            objects[GeneralizedIndex(k // 2)] = hash(
                objects[GeneralizedIndex((k | 1) ^ 1)] +
                objects[GeneralizedIndex(k | 1)]
            )
            keys.append(GeneralizedIndex(k // 2))
        pos += 1
    return objects[GeneralizedIndex(1)]
```

```python
def verify_merkle_multiproof(leaves: Sequence[Bytes32],
                             proof: Sequence[Bytes32],
                             indices: Sequence[GeneralizedIndex],
                             root: Root) -> bool:
    return calculate_multi_merkle_root(leaves, proof, indices) == root
```

Note that the single-item proof is a special case of a multi-item proof; a valid single-item proof verifies correctly when put into the multi-item verification function (making the natural trivial changes to input arguments, `index -> [index]` and `leaf -> [leaf]`). Note also that `calculate_merkle_root` and `calculate_multi_merkle_root` can be used independently to compute the new Merkle root of a proof with leaves updated.
