# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 22:36:08 2021

@author: zefyr
"""

import gamePlay
import numpy as np

g = gamePlay.GamePlay(0, 1, 10, 0, 0)

g.playSpace.horizontalAxis = np.array([-1, 0, 0])
g.playSpace.verticalAxis = np.array([0, 1, 0])
g.playSpace.players[0]['position'] = np.array([1, 1, 10])
g.playSpace.movePlayer(0, '<', spacesOverride = 1)