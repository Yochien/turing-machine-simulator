import argparse
from dataclasses import dataclass
from enum import Enum


parser = argparse.ArgumentParser(prog = "Turing Simulator",
                                 description = "Computes the results of a Turing State Machine written in the syntax from https://turingmachinesimulator.com.")
parser.add_argument("-f", "--input_file", type = str, help = "The exact location and name of the input file which defines the Turing Machine.", required = True)
parser.add_argument("-i", "--input", type = str, help = "The input string for the Turing Machine that represents its initial tape state.", required = True)
args = parser.parse_args()
INPUT_FILE_NAME = args.input_file
TURING_MACHINE_INPUT = args.input


class TMConfigError(Exception):
    """Exception related to parsing the Turing Machine input file."""
    pass


class Direction(Enum):
    """Enum that defines the character mapping between Turing Machine tape directions and input file syntax."""
    LEFT = "<"
    RIGHT = ">"
    HALT = "-"


@dataclass(frozen=True)
class DeltaFunction():
    """Data class that represents a Turing Machine delta function."""
    current_state: str
    read_symbol: str
    new_state: str
    write_symbol: str
    direction: Direction


@dataclass
class TuringMachineConfig():
    """Data class that represents the properties of a Turing Machine used by https://turingmachinesimulator.com."""
    initial_state: str
    accept_states: list[str]
    name: str = "Turing Machine"


class TuringMachine:
    REJECT_STATE = "REJECT"

    def __init__(self, config: TuringMachineConfig, delta_functions: set[DeltaFunction], input: str):
        self.name = config.name
        self.initial_state = config.initial_state
        self.accept_states = config.accept_states
        self.accept_states.append(TuringMachine.REJECT_STATE)
        self.delta_functions = delta_functions
        self.tape = list(input)

        self.current_state = self.initial_state
        self.tape_loc = 0

    def execute(self) -> str:
        current_char = "_"
        if self.tape_loc < len(self.tape) and self.tape_loc >= 0:
            current_char = self.tape[self.tape_loc]

        for delta_function in self.delta_functions:
            if delta_function.current_state == self.current_state and delta_function.read_symbol == current_char:
                if self.tape_loc == -1:
                    self.tape.insert(0, current_char)
                elif self.tape_loc == len(self.tape):
                    self.tape.append(current_char)
                else:
                    self.tape[self.tape_loc] = delta_function.write_symbol

                if delta_function.direction == Direction.LEFT:
                    self.tape_loc = self.tape_loc - 1
                elif delta_function.direction == Direction.RIGHT:
                    self.tape_loc = self.tape_loc + 1

                self.current_state = delta_function.new_state
                return
        self.current_state = TuringMachine.REJECT_STATE


def is_TM_property(line: str) -> bool:
    """Returns true if the line follows the syntax for a Turing Machine property."""
    return line.find(":") >= 0


def build_TM_config(file: list[str]) -> TuringMachineConfig:
    lines = [line for line in file if is_TM_property(line)]

    if len(lines) > 3 or len(lines) < 2:
        raise TMConfigError("Wrong number of required TM properties.")

    default_config = {
        "name": "Turing Machine",
        "init": None,
        "accept": []
    }

    for line in lines:
        key, value = (element.strip() for element in line.split(":"))
        key = key.lower()
        if key == "accept":
            value = [value.strip() for value in value.split(",")]

        if key in default_config:
            default_config[key] = value
        else:
            raise TMConfigError(f"Encountered unknown property in line: {line}")

    if default_config["init"] is None:
        raise TMConfigError("Initial state must be defined.")
    if len(default_config["accept"]) < 1:
        raise TMConfigError("At least one accept state must be defined.")

    return TuringMachineConfig(default_config["init"], default_config["accept"], default_config["name"])


def build_delta_functions(file: list[str]) -> set[DeltaFunction]:
    """Parses the input file for valid delta functions and returns them."""

    states = set()
    lines = [line.strip() for line in file if not is_TM_property(line)]

    if not lines:
        raise TMConfigError("No delta functions found.")
    if len(lines) % 2 != 0:
        raise TMConfigError("Wrong number of lines for defining Turing Machines delta functions.")

    for _ in range(len(lines) // 2):
        current_state, read_symbol = [value.strip() for value in lines.pop(0).split(",")]
        new_state, write_symbol, direction = [value.strip() for value in lines.pop(0).split(",")]

        if len(read_symbol) != 1:
            raise TMConfigError(f"Read symbol for delta function must be one character, but was {read_symbol}")
        if len(write_symbol) != 1:
            raise TMConfigError(f"Write symbol for delta function must be one character, but was {write_symbol}")

        try:
            direction = Direction(direction)
        except ValueError:
            raise TMConfigError(f"Invalid direction for state: {direction}")

        states.add(DeltaFunction(current_state, read_symbol, new_state, write_symbol, direction))

    return states


def load_file() -> list[str]:
    """Returns the input file as a list of its lines without comments or blank lines."""

    def is_comment(line: str) -> bool:
        return line.startswith("//") or line.isspace() or not line

    with open(INPUT_FILE_NAME, mode="r") as file:
        return [line.strip() for line in file if not is_comment(line)]


def main():
    file = load_file()
    config = build_TM_config(file)
    deltas = build_delta_functions(file)
    tm = TuringMachine(config, deltas, TURING_MACHINE_INPUT)
    tm.execute()
    while tm.current_state not in tm.accept_states:
        tm.execute()
    print(f"Ended in state {tm.current_state}\nTape was: {tm.tape}\nTape head was at position {tm.tape_loc + 1}")


main()
