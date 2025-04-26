from dataclasses import dataclass
from typing import Tuple, List
import numpy as np


@dataclass
class GridSquare:
    row: int
    col: int
    image: np.ndarray
    corners: List[Tuple[int, int]]
