import random

from Classes.Constants import MaterialConstants, BuildConstants
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface
from math import floor
from .helpers import *

class EdoAgent(AgentInterface):
    """
    Es necesario poner super().nombre_de_funcion() para asegurarse de que coge la función del padre
    """
    def __init__(self, bot_id):
        
        super().__init__(bot_id)
        self.turn_counter = 0 # contador de turnos
        self.goals = [ # lista con orden de prioridades de los objetivos inmediatos
            "build_town",
            "build_town",
            "build_town",
            "build_town",
            "build_city",
            "build_city",
            "build_city",
            "build_city",
        ]
        self.traded = False

    def get_mat(self):
        return materials_to_mat(self.hand.resources)

    # TODO: P1 
    def on_trade_offer(self, board_instance, incoming_trade_offer=TradeOffer(), player_making_offer=int):
        # print(building_costs)
        
        # answer = random.randint(0, 2)
        # if answer:
        #     if answer == 2:
        #         gives = Materials(random.randint(0, self.hand.resources.cereal),
        #                           random.randint(0, self.hand.resources.mineral),
        #                           random.randint(0, self.hand.resources.clay),
        #                           random.randint(0, self.hand.resources.wood),
        #                           random.randint(0, self.hand.resources.wool))
        #         receives = Materials(random.randint(0, self.hand.resources.cereal),
        #                              random.randint(0, self.hand.resources.mineral),
        #                              random.randint(0, self.hand.resources.clay),
        #                              random.randint(0, self.hand.resources.wood),
        #                              random.randint(0, self.hand.resources.wool))
        #         return TradeOffer(gives, receives)
        #     else:
        #         return True
        # else:
            return False

    def on_turn_start(self):
        self.traded = False
        self.turn_counter += 1

        if not self.goals:
            self.goals = ["build_city"]

        if self.goals[0] == "build_city" and not self.board.valid_city_nodes(self.id):
            self.goals.insert(0, "build_town")
        elif self.goals[0] == "build_town" and not self.board.valid_town_nodes(self.id):
            self.goals.insert(0, "build_road")

        # if len(self.development_cards_hand.check_hand()) and random.randint(0, 1):
        #     return self.development_cards_hand.select_card_by_id(self.development_cards_hand.hand[0].id)
        return None

    # DONE
    def on_having_more_than_7_materials_when_thief_is_called(self):
        excess_count_rule = int(floor(self.hand.get_total()/2))
        excess = excess_materials(self.get_mat(), self.goals[:1])
        excess_count_excess = sum(excess)
        for i in range(min(excess_count_rule, excess_count_excess)):
            max_index = excess.index(max(excess))
            self.hand.remove_material(max_index, 1)
        return self.hand

    def on_moving_thief(self):
        terrain = random.randint(0, 18)
        player = -1
        for node in self.board.terrain[terrain]['contacting_nodes']:
            if self.board.nodes[node]['player'] != -1:
                player = self.board.nodes[node]['player']
        return {'terrain': terrain, 'player': player}

    def on_turn_end(self):
        # if len(self.development_cards_hand.check_hand()) and random.randint(0, 1):
        #     return self.development_cards_hand.select_card_by_id(self.development_cards_hand.hand[0].id)
        return None

    def on_commerce_phase(self):
        if self.traded:
            return None

        # TODO: comercion con banca
        # if self.hand.resources.cereal >= 4:
        #     return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.MINERAL}
        # if self.hand.resources.mineral >= 4:
        #     return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.CEREAL}
        # if self.hand.resources.clay >= 4:
        #     return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.CEREAL}
        # if self.hand.resources.wood >= 4:
        #     return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.CEREAL}
        # if self.hand.resources.wool >= 4:
        #     return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.CEREAL}
        # return None
        excess, needed = create_exchange(self.get_mat(), self.goals[:1])
        if sum(excess) == 0 or sum(needed) == 0:
            return None
        
        excess_index = weighted_material_choice(excess)
        gives = index_to_mat(excess_index)
        _gives = Materials(*gives)

        needed_index = weighted_material_choice(needed)
        receives = index_to_mat(needed_index)
        _receives = Materials(*receives)

        self.traded = True
        # print(f"({self.turn_counter}) {self.goals[0]}: {gives} -> {receives}")
        return TradeOffer(_receives, _gives)

    def on_build_phase(self, board_instance):
        self.board = board_instance

        if not self.goals:
            self.goals = ["build_city"]
            
        goal = self.goals[0]
        
        if goal == "build_town" and self.hand.resources.has_this_more_materials('town'):
            valid_nodes = self.board.valid_town_nodes(self.id)
            if len(valid_nodes):
                # TODO: mejorar selección
                town_node = random.randint(0, len(valid_nodes) - 1)
                self.goals.remove(goal)
                return {'building': BuildConstants.TOWN, 'node_id': valid_nodes[town_node]}
            
        elif goal == "build_city" and self.hand.resources.has_this_more_materials('city'):
            valid_nodes = self.board.valid_city_nodes(self.id)
            # TODO: mejorar selección
            if len(valid_nodes):
                city_node = random.randint(0, len(valid_nodes) - 1)
                self.goals.remove(goal)
                return {'building': BuildConstants.CITY, 'node_id': valid_nodes[city_node]}
        
        # TODO: se puede mejorar escogiendo en base a los recursos
        elif goal == "build_road" and self.hand.resources.has_this_more_materials('road'):
            road_ends = get_road_ends(self.board, self.id)
            for end in road_ends:
                adjacent_roads = get_adjacent_road(self.board, end, self.id)
                for adjacent in adjacent_roads:
                    self.goals.remove(goal)
                    return {'building': BuildConstants.ROAD,
                            'node_id': adjacent['starting_node'],
                            'road_to': adjacent['finishing_node']}


        elif goal == "buy_card" and self.hand.resources.has_this_more_materials('card'):
            self.goals.remove(goal)
            return {'building': BuildConstants.CARD}

        return None

    def on_game_start(self, board_instance):
        return super().on_game_start(board_instance)

    def on_monopoly_card_use(self):
        material = random.randint(0, 4)
        return material

    # noinspection DuplicatedCode
    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            while True:
                road_node = random.randint(0, len(valid_nodes) - 1)
                road_node_2 = random.randint(0, len(valid_nodes) - 1)
                if road_node != road_node_2:
                    return {'node_id': valid_nodes[road_node]['starting_node'],
                            'road_to': valid_nodes[road_node]['finishing_node'],
                            'node_id_2': valid_nodes[road_node_2]['starting_node'],
                            'road_to_2': valid_nodes[road_node_2]['finishing_node'],
                            }
        elif len(valid_nodes) == 1:
            return {'node_id': valid_nodes[0]['starting_node'],
                    'road_to': valid_nodes[0]['finishing_node'],
                    'node_id_2': None,
                    'road_to_2': None,
                    }
        return None

    def on_year_of_plenty_card_use(self):
        material, material2 = random.randint(0, 4), random.randint(0, 4)
        return {'material': material, 'material_2': material2}
