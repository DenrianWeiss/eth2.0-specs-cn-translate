from eth2spec.phase0 import spec as spec_phase0
from eth2spec.altair import spec as spec_altair
from eth2spec.test.context import PHASE0, ALTAIR

from eth2spec.gen_helpers.gen_from_tests.gen import run_state_test_generators


specs = (spec_phase0, spec_altair)


if __name__ == "__main__":
    phase_0_mods = {key: 'eth2spec.test.phase0.sanity.test_' + key for key in [
        'blocks',
        'slots',
    ]}
    altair_mods = {**{key: 'eth2spec.test.altair.sanity.test_' + key for key in [
        'blocks',
    ]}, **phase_0_mods}  # also run the previous phase 0 tests

    all_mods = {
        PHASE0: phase_0_mods,
        ALTAIR: altair_mods,
    }

    run_state_test_generators(runner_name="sanity", specs=specs, all_mods=all_mods)
