# Turing Machine Simulator

A command-line Turing Machine simulator implemented in Python3 that follows the syntax from [turingmachinesimulator.com](https://turingmachinesimulator.com). Uses `argparse` to manage its inputs, so run the program with the `-h` or `--help` flags for more details.

## Limitations

This implementation is limited in that:

- it can only handle drifting from the initial size of the tape by one on either end,
- and it does not attempt to end the simulation if it runs forever or halts.
  - The simulator would churn forever on a looping state machine.
  - The simulator would wait forever on a halted state if it was not also an accept state.

**This implementation was enough to satisfy my curiosity with the topic**, but it could be extended to allow users to fix the above limitations.
