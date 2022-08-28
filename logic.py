import numpy as np
# import time
from typing import List, Dict


def get_info() -> dict:
    return {
        "apiversion": "1",
        "author": "timothycho",  # TODO: Your Battlesnake Username
        "color": "#3E338F",  # TODO: Personalize
        "head": "caffeine",  # TODO: Personalize
        "tail": "hook",  # TODO: Personalize
    }


def choose_move(data: dict) -> str:
    # start timer for choose_move
    # start_time = time.time()

    my_snake = data["you"]
    my_head = my_snake["head"]
    my_body = my_snake["body"]
    my_health = my_snake["health"]

    food = data["board"]["food"]
    snakes = data["board"]["snakes"]

    possible_moves = ["up", "down", "left", "right"]
    possible_moves = avoid_my_neck(my_body, possible_moves)
    possible_moves = avoid_walls(my_body, possible_moves)
    possible_moves = avoid_snakes(my_head, snakes, possible_moves, data["you"]["length"])

    num_moves = len(possible_moves[0])
    # find food a bit earlier when uneven length to avoid head snipes
    if (my_health < 33 or (my_health < 38 and data["you"]["length"] % 2 == 1)) and num_moves != 0:
        move = find_food(my_head, data["board"]["food"], possible_moves[0], possible_moves[1])
    else:
        move = chase_tail(my_head, my_body, possible_moves[0], possible_moves[1])

    # end timer for choose_move, print elapsed time
    # end_time = time.time()
    # elapsed = end_time - start_time
    # print(f"Choose Move Time: {round(elapsed * 1000, 2)}ms")
    print(f"MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move


def avoid_my_neck(my_body: dict, possible_moves: List[str]) -> List[str]:
    my_head = my_body[0]  # The first body coordinate is always the head
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves


def avoid_snakes(my_head, snakes, possible_moves, length):
    # create grid
    grid = np.zeros((11, 11), dtype=int)  # switch to numpy since slightly bit faster

    # moves that will lead to potential head to head collisions
    panic_moves = []

    for snakeIndex in range(len(snakes)):
        # Adds the possible ways a snake head could move if it has more health
        if snakes[snakeIndex]["body"][0] != my_head and snakes[snakeIndex]["length"] >= length:
            if snakes[snakeIndex]["body"][0]["x"] - 1 >= 0:
                grid[snakes[snakeIndex]["body"][0]["y"]][snakes[snakeIndex]["body"][0]["x"] - 1] = 2
            if snakes[snakeIndex]["body"][0]["x"] + 1 <= 10:
                grid[snakes[snakeIndex]["body"][0]["y"]][snakes[snakeIndex]["body"][0]["x"] + 1] = 2
            if snakes[snakeIndex]["body"][0]["y"] - 1 >= 0:
                grid[snakes[snakeIndex]["body"][0]["y"] - 1][snakes[snakeIndex]["body"][0]["x"]] = 2
            if snakes[snakeIndex]["body"][0]["y"] + 1 <= 10:
                grid[snakes[snakeIndex]["body"][0]["y"] + 1][snakes[snakeIndex]["body"][0]["x"]] = 2

        for bodyIndex in range(len(snakes[snakeIndex]["body"]) - 1):
            # Adds every part except the tail
            grid[snakes[snakeIndex]["body"][bodyIndex]["y"]][snakes[snakeIndex]["body"][bodyIndex]["x"]] = 1

        # Remove killing moves using grid
        # removed the try/excepts since out of index moves were removed earlier with avoid_walls()

        if "up" in possible_moves:
            if grid[my_head["y"] + 1][my_head["x"]] >= 1:
                possible_moves.remove("up")
                if grid[my_head["y"] + 1][my_head["x"]] == 2:
                    panic_moves.append("up")

        if "down" in possible_moves:
            if grid[my_head["y"] - 1][my_head["x"]] >= 1:
                possible_moves.remove("down")
                if grid[my_head["y"] - 1][my_head["x"]] == 2:
                    panic_moves.append("down")

        if "left" in possible_moves:
            if grid[my_head["y"]][my_head["x"] - 1] >= 1:
                possible_moves.remove("left")
                if grid[my_head["y"]][my_head["x"] - 1] == 2:
                    panic_moves.append("left")

        if "right" in possible_moves:
            if grid[my_head["y"]][my_head["x"] + 1] >= 1:
                possible_moves.remove("right")
                if grid[my_head["y"]][my_head["x"] + 1] == 2:
                    panic_moves.append("right")

    return [possible_moves, panic_moves]

    # if {"x": my_head["x"], "y": my_head["y"]} in my_body:
    #   my_body.remove({"x": my_head["x"], "y": my_head["y"]})


def find_food(my_head, food, possible_moves, panic_moves):
    closest_food = {"x": 5, "y": 5}
    closest_dist = 50
    print("Find Food")
    for i in range(len(food)):
        dist = abs(my_head["x"] - food[i]["x"]) + abs(my_head["y"] - food[i]["y"])
        # print(dist, closest_dist)
        if dist < closest_dist:
            closest_dist = dist
            closest_food = food[i]

    x_diff = abs(my_head["x"] - closest_food["x"])
    y_diff = abs(my_head["y"] - closest_food["y"])

    execute = True
    if x_diff > y_diff:
        execute = False
        if my_head["x"] > closest_food["x"]:
            choice = "left"
        else:
            choice = "right"

        if choice not in possible_moves:
            execute = True

    if execute:
        if my_head["y"] > closest_food["y"]:
            choice = "down"
        else:
            choice = "up"

        if choice not in possible_moves:
            print("FindFood Can't Move -> Picks First Moves")
            return possible_moves[0]

    return choice


def chase_tail(my_head, my_body, possible_moves, panic_moves):
    my_neck = my_body[1]
    my_tail = my_body[-1]

    xDiff = abs(my_head["x"] - my_tail["x"])
    yDiff = abs(my_head["y"] - my_tail["y"])
    print("Tail Chase")

    # if no safe moves, use moves with potential head to head collision
    if len(possible_moves) == 0:
        possible_moves = panic_moves
    # removes option to move straight when able to turn (tries to keep turning)
    if len(possible_moves) > 2:
        if my_head["y"] > my_neck["y"] and "up" in possible_moves:
            possible_moves.remove("up")
        elif my_head["y"] < my_neck["y"] and "down" in possible_moves:
            possible_moves.remove("down")
        elif my_head["x"] > my_neck["x"] and "right" in possible_moves:
            possible_moves.remove("right")
        elif my_head["x"] < my_neck["x"] and "left" in possible_moves:
            possible_moves.remove("left")

    execute = True
    if xDiff > yDiff:
        execute = False
        if my_head["x"] > my_tail["x"]:
            choice = "left"
        else:
            choice = "right"

        if choice not in possible_moves:
            execute = True

    if execute:
        if my_head["y"] > my_tail["y"]:
            choice = "down"
        else:
            choice = "up"

        if choice not in possible_moves:
            if len(possible_moves) > 0:
                print("ChaseTail Can't Move -> Picks First Moves")
                return possible_moves[0]
            else:  #
                print("None")
                choice = None

    return choice


def avoid_walls(my_body: dict, possible_moves: List[str]) -> List[str]:
    my_head = my_body[0]
    if my_head["x"] in [0, 10] or my_head["y"] in [0, 10]:
        # if move would go into wall, remove it
        if my_head["x"] + 1 > 10 and "right" in possible_moves:
            possible_moves.remove("right")
        if my_head["x"] - 1 < 0 and "left" in possible_moves:
            possible_moves.remove("left")
        if my_head["y"] + 1 > 10 and "up" in possible_moves:
            possible_moves.remove("up")
        if my_head["y"] - 1 < 0 and "down" in possible_moves:
            possible_moves.remove("down")
    return possible_moves

