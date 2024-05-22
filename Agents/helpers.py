from Classes.Constants import *
from Classes.Materials import Materials
from typing import List, Tuple, Set, FrozenSet
import random
from typing import NamedTuple
from functools import reduce
from Classes.Board import Board

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

class Road(NamedTuple):
    vertex: FrozenSet[int]
    owner: int

    def __str__(self):
        return f"{self.owner}: {self.vertex}"

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

def msub(m1: Mat, m2: Mat) -> Mat: 
    """ Element by element subtraction """ 
    return Mat(*(x - y for x, y in zip(m1, m2)))

def madd(m1: Mat, m2: Mat) -> Mat:
    """ Element by element addition """	
    return Mat(*(x + y for x, y in zip(m1, m2)))

def mpos(m: Mat) -> Mat:
    """ filter non-positive values"""
    return Mat(*(x if x > 0 else 0 for x in m))

def index_to_mat(index: int, value: int = 1) -> Mat:
    """
    Converts an index to a Mat object.
    """
    return Mat(*[value if i == index else 0 for i in range(5)])


# Materials helpers

def materials_to_mat(materials: Materials) -> Mat:
    """ Converts a Materials object to a Mat object. """
    return Mat(materials.cereal, materials.mineral, materials.clay, materials.wood, materials.wool)

def mat_to_materials(mat: Mat) -> Materials:
    """ Converts a Mat object to a Materials object. """
    return Materials(*mat)

def missing_materials(owned: Mat, wanted: Mat) -> Mat:
    """ Calculates the missing materials based on the owned materials and the desired materials. """
    return mpos(msub(wanted, owned))

def excess_materials(owned: Mat, goal_list: List[str]) -> Mat:
    """ Calculates the excess materials based on the owned materials and the desired goals. """
    excess = reduce(msub, [goals_costs[goal] for goal in goal_list], owned)
    return mpos(excess)

def needed_materials(goal_list: List[str]) -> Mat:
    """ Calculates the needed materials based on the desired goals. """	
    wanted = reduce(madd, [goals_costs[goal] for goal in goal_list], Mat(0, 0, 0, 0, 0))
    return wanted


# exchange helpers

def weighted_material_choice(mat: Mat) -> int:
    """ Chooses an index based on the materials. """
    list = [0] * mat[0] + [1] * mat[1] + [2] * mat[2] + [3] * mat[3] + [4] * mat[4]
    return random.choice(list)

def create_exchange(owned: Mat, goal_list: List[str]) -> Tuple[Mat, Mat]:
    """ Creates a trade offer based on the owned materials and the desired goals. """
    excess = excess_materials(owned, goal_list)
    needed = needed_materials(goal_list)
    missing = missing_materials(owned, needed)
    return excess, missing

def goal_distance(owned: Mat, goal_list: List[str]) -> int:
    """ Calculates the distance to the goal based on the owned materials and the desired goals. """
    needed = needed_materials(goal_list)
    missing = missing_materials(owned, needed)
    return sum(missing)


# Map helpers
def get_roads(board: Board, player_id = None) -> Set[Road]:
    """ Returns a list of all roads on the board. """
    nodes = board.nodes
    roads = set()
    for node in nodes:
        roads.update({
            Road(frozenset([node["id"],road["node_id"]]), road["player_id"])
            for road
            in node["roads"]
            if road["player_id"] == player_id or player_id == None
        })
    return roads
