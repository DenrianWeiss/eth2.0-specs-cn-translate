<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Operations tests](#operations-tests)
  - [Test case format](#test-case-format)
    - [`meta.yaml`](#metayaml)
    - [`pre.ssz_snappy`](#pressz_snappy)
    - [`<input-name>.ssz_snappy`](#input-namessz_snappy)
    - [`post.ssz_snappy`](#postssz_snappy)
  - [Condition](#condition)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Operations tests

The different kinds of operations ("transactions") are tested individually with test handlers.

## Test case format

### `meta.yaml`

```yaml
description: string    -- Optional description of test case, purely for debugging purposes.
                          Tests should use the directory name of the test case as identifier, not the description.
bls_setting: int       -- see general test-format spec.
```

### `pre.ssz_snappy`

An SSZ-snappy encoded `BeaconState`, the state before applying the operation.

### `<input-name>.ssz_snappy`

An SSZ-snappy encoded operation object, e.g. a `ProposerSlashing`, or `Deposit`.

### `post.ssz_snappy`

An SSZ-snappy encoded `BeaconState`, the state after applying the operation. No value if operation processing is aborted.


## Condition

A handler of the `operations` test-runner should process these cases,
 calling the corresponding processing implementation.
This excludes the other parts of the block-transition.

Operations:

| *`operation-name`*      | *`operation-object`*  | *`input name`*       | *`processing call`*                                             |
|-------------------------|-----------------------|----------------------|-----------------------------------------------------------------|
| `attestation`           | `Attestation`         | `attestation`        | `process_attestation(state, attestation)`                       |
| `attester_slashing`     | `AttesterSlashing`    | `attester_slashing`  | `process_attester_slashing(state, attester_slashing)`           |
| `block_header`          | `BeaconBlock`         | **`block`**          | `process_block_header(state, block)`                            |
| `deposit`               | `Deposit`             | `deposit`            | `process_deposit(state, deposit)`                               |
| `proposer_slashing`     | `ProposerSlashing`    | `proposer_slashing`  | `process_proposer_slashing(state, proposer_slashing)`           |
| `voluntary_exit`        | `SignedVoluntaryExit` | `voluntary_exit`     | `process_voluntary_exit(state, voluntary_exit)`                 |
| `sync_aggregate`        | `SyncAggregate`       | `sync_aggregate`     | `process_sync_committee(state, sync_aggregate)` (new in Altair) |

Note that `block_header` is not strictly an operation (and is a full `Block`), but processed in the same manner, and hence included here.

The resulting state should match the expected `post` state, or if the `post` state is left blank,
 the handler should reject the input operation as invalid.
