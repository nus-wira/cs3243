# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Actions, Directions, Grid
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestItem(pos, itemGrid, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a item at this location then exit
        if itemGrid[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no item found
    return None


class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestItem((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        features.divideAll(10.0)
        return features

class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """
    def getFeatures(self, state, action):
        "*** YOUR CODE HERE ***"
        """
        Returns simple features for a basic reflex Pacman:
        - what is on next step
            Food
            Capsule
            Scared Ghost
            Ghost
            PS: the Ghosts and Scared Ghosts can exist together
        - What is far away
        """
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        capsules = state.getCapsules()
        features = util.Counter()

        features["bias"] = 1.0

        # calculate the position of the pacman after this action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # set up the ghost and capsule grids
        not_scared_ghostsPosList = []
        not_scared_ghostsGrid = Grid(food.width, food.height)
        scared_ghostsPosList = []
        scared_ghostsGrid = Grid(food.width, food.height)
        for i in range(len(ghosts)):
            if state.getGhostStates()[i].scaredTimer > 0:
                scared_ghostsPosList.append(ghosts[i])
                scared_ghostsGrid[int(ghosts[i][0])][int(ghosts[i][1])] = True
            else:
                not_scared_ghostsPosList.append(ghosts[i])
                scared_ghostsGrid[int(ghosts[i][0])][int(ghosts[i][1])] = True
        
        capsuleGrid = Grid(food.width, food.height)
        capsulePosList = []
        for i in range(len(capsules)):
            capsuleGrid[int(capsules[i][0])][int(capsules[i][1])] = True
            capsulePosList.append(capsules[i])
        
        # get the the features for ghosts in different states
        if len(scared_ghostsPosList) > 0:
            if scared_ghostsGrid[next_x][next_y]:
                features["eats-ghost"] = 1.0

            dist_ghost = closestItem((next_x, next_y), scared_ghostsGrid, walls)
            if dist_ghost is not None:
                features["closest-scared-ghost"] = (float(dist_ghost) / (walls.width * walls.height) * 20)

        if len(not_scared_ghostsPosList) > 0:
            # if there is ghosts around, add the capule feature
            features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in not_scared_ghostsPosList)
            # if there is no ghosts then add the food feature
            if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
                features["eats-food"] = 1.0

            if not features["#-of-ghosts-1-step-away"] and capsuleGrid[next_x][next_y]:
                features["eats-capule"] = 1.0
            
            dist_cap = closestItem((next_x, next_y), capsuleGrid, walls)
            if dist_cap is not None:
                features["closest-capsule"] = (float(dist_cap) / (walls.width * walls.height))

        if len(not_scared_ghostsPosList) == 0 and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist_food = closestItem((next_x, next_y), food, walls)
        if dist_food is not None:
            features["closest-food"] = float(dist_food) / (walls.width * walls.height)

        features.divideAll(10.0)
        return features