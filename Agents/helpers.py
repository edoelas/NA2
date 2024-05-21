from Classes.Constants import *
from Classes.Materials import Materials
from typing import List, Tuple
import random
from collections import namedtuple
from typing import NamedTuple

class Mat(NamedTuple):
    ce: int
    mi: int
    cl: int
    wd: int
    wl: int
    
    def __str__(self):
        material_icons = ["🥖", "🪨", "🧱", "🪵", "🧶"]
        material_tuples = list(zip(self, material_icons))
        mls = [str(t[0]).rjust(2)+t[1] for t in material_tuples]
        return " ".join(mls)


TOWN = BuildConstants.TOWN
CITY = BuildConstants.CITY
ROAD = BuildConstants.ROAD   
CARD = BuildConstants.CARD

CEREAL = MaterialConstants.CEREAL
MINERAL = MaterialConstants.MINERAL
CLAY = MaterialConstants.CLAY
WOOD = MaterialConstants.WOOD
WOOL = MaterialConstants.WOOL

# cereal, mineral, clay, wood, wool
building_costs = {
    TOWN: Mat(1, 0, 1, 1, 1), # {CEREAL: 1, CLAY: 1, WOOD: 1, WOOL: 1},
    CITY: Mat(2, 3, 0, 0, 0), # {CEREAL: 2, MINERAL: 3},
    ROAD: Mat(0, 0, 1, 1, 0), # {CLAY: 1, WOOD: 1},
    CARD: Mat(1, 1, 0, 0, 1), # {CEREAL: 1, WOOL: 1, MINERAL: 1}
}

goals_costs = {
    "build_town": building_costs[TOWN],
    "build_city": building_costs[CITY],
    "build_road": building_costs[ROAD],
    "buy_card": building_costs[CARD]
}



# List helpers

def msub(m1: Mat, m2: Mat) -> Mat: # element by element subtraction
    return Mat(*(x - y for x, y in zip(m1, m2)))

def madd(m1: Mat, m2: Mat) -> Mat: # element by element addition
    return Mat(*(x + y for x, y in zip(m1, m2)))

def mpos(m: Mat) -> Mat: # return positives only
    return Mat(*(x if x > 0 else 0 for x in m))

# def index_to_list(index: int, len: int = 5, value: int = 1):
#     """
#     Converts an index to a list with the value at the index.
#     """
#     return [value if i == index else 0 for i in range(len)]

# Materials helpers

def materials_to_mat(materials: Materials) -> Mat: # Converts a Materials object to a Mat object.
    return Mat(materials.cereal, materials.mineral, materials.clay, materials.wood, materials.wool)

def mat_to_materials(mat: Mat) -> Materials: # Converts a Mat object to a Materials object.
    return Materials(*mat)

def missing_materials(owned: Mat, wanted: Mat) -> Mat: # Calculates the missing materials based on the owned materials and the desired materials.
    return mpos(msub(wanted, owned))

def excess_materials(owned: Mat, goal_list: List[str]) -> Mat: # Calculates the excess materials based on the owned materials and the desired goals.
    excess = owned
    for goal in goal_list:
        goal_materials = goals_costs[goal]
        excess = msub(excess, goal_materials)

    return mpos(excess)

# exchange helpers

def weighted_material_choice(mat: Mat) -> int: # Chooses an index based on the materials
    list = [0] * mat[0] + [1] * mat[1] + [2] * mat[2] + [3] * mat[3] + [4] * mat[4]
    return random.choice(list)

def create_exchange(owned: Mat, goal_list: List[str]):
    """
    Creates a trade offer based on the owned materials and the desired goals.
    """
    excess = excess_materials(owned, goal_list)
    wanted = [0, 0, 0, 0, 0]
    for goal in goal_list:
        goal = material_to_list(goals_costs[goal])
        wanted = addl(wanted, goal)
    needed = missing_materials(owned, Materials(*wanted))
    return excess, needed


def goal_distance(owned: Materials, goal: str):
    """
    Calculates the distance to the goals based on the owned materials and the desired goal.
    """
    needed = missing_materials(owned, goals_costs[goal])
    return sum(material_to_list(needed))