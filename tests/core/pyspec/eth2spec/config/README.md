<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Eth2 config util](#eth2-config-util)
  - [Usage:](#usage)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Eth2 config util

For configuration, see [Configs documentation](../../../../../configs/README.md).

## Usage:

```python
configs_path = 'configs/'

...

from eth2spec.config import config_util
from eth2spec.phase0 import spec
from importlib import reload
config_util.prepare_config(configs_path, 'mainnet')
# reload spec to make loaded config effective
reload(spec)
```

WARNING: this overwrites globals, make sure to prevent accidental collisions with other usage of the same imported specs package.
