from itertools import product
from enum import Enum

class Amplitude(Enum):
    Small = 1
    Large = 2

class BaseAngle(Enum):
    Front = 1
    Side = 2

class Distance(Enum):
    Close = 1
    Far = 2

class Movement(Enum):
    Yes = 1
    No = 2

class Room(Enum):
    Concert = 1
    Sports = 2

class Source(Enum):
    Human = 1
    Loudspeaker = 2

def get_recording_combinations(number_of_repetitions: int = 3):
    combinations = product(Amplitude, BaseAngle, Distance, range(1, number_of_repetitions + 1))
    return [{"Amplitude": amplitude.name,
          "Base Angle": baseAngle.name,
          "Distance": distance.name,
          "Repetition": repetition} for amplitude, baseAngle, distance, repetition in combinations]