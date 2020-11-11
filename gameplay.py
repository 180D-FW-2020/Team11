ROTATION_COOLDOWN = 20

class GamePlay:
    def __init__(self, primaryNode = True):
    def __init__(self, numPlayers, primaryNode = True):
        try:
            if primaryNode:
                args = self.settings()
            else: args = (0, 0, 0, 0)
            self.startPlaySpace(args)
            else: args = (numPlayers, 0, 0, 0)

            self.playSpace = PlaySpace(numPlayers, args)
        except:
            print("An error occurred initializing GamePlay")

    def settings(self):
        try:
            print("This will prompt a player for the game settings")
            # use mic to get edgeLength, numObstacles, numPowerups, this is dummy
            numPlayers, edgeLength, numObstacles, numPowerups = (0, 0, 0, 0)
            return numPlayers, edgeLength, numObstacles, numPowerups
        '''
        This prompts the central node player for game settings: edgelength,
        number of obstacles, and number of powerups. Number of players too
        would be ideal.
        
        Returns those settings.
        '''
        try:
            # These are dummy values
            edgeLength, numObstacles, numPowerups = (0, 0, 0)
            return edgeLength, numObstacles, numPowerups
        except:
            print("An error occurred getting settings")

    def startPlaySpace(self, args):
        try:
            self.playSpace = PlaySpace(args)
        except:
            print("An error occurred generating the playspace")
    def unpack(self):
        '''
        Unpacks message from a pc or pi containing a player number with a
        rotation or direction.
            
    def getPlayerInput(self):
        Returns playerId, rotation, and direction.
        '''
        try:
            print("This will get package date from players and", 
                  "return a player number with a rotation",
                  "or direction")
            #return rotation, direction
            # These are dummy values
            playerId, rotation, direction = (0, 0, 0)
            return playerId, rotation, direction
        except:
            print("An error occurred getting player input")

    def updateAllNodes(self):
        try:
            print("This sends a message to all nodes with the current playspace",
                  "and player data, and clears nodes to send new messages")
    def pack(self):
        '''
        Packs message for pc and pi containing updates for the display, permission
        to send more messages, or both. Permission to send more messages is
        specific to the node: pc may have permission while pi is still on cooldown.
        
        Returns message for transmission.
        '''
        try:
            #0 is a dummy value, this should be updated with message packing code
            message = 0
            return message
        except:
            print("An error occurred updating nodes")

class PlaySpace:
    def __init__(self, numPlayers, edgeLength, numObstacles, numPowerups):
        try:
            self.edgeLength = edgeLength
            self.obstacles = []
            self.powerUps = []
            self.message = ""
            self.sender = Transmitter("team11/nodetoPC")
            #sender.update("all player xyz and it, plane of referance")
            if numObstacles: self.placeObstacles(numObstacles)
            if numPowerups: self.placePowerUps(numPowerups)

@@ -62,92 +78,128 @@ def __init__(self, numPlayers, edgeLength, numObstacles, numPowerups):

            if numPlayers:
                self.numPlayers = numPlayers
                self.playersNotIt = self.placePlayers(numPlayers)
                self.players, self.playersNotIt = self.placePlayers(numPlayers)

        except:
            print("An error occurred initializing PlaySpace")

    def placePlayers(self, numPlayers):
        '''
        Randomly places players in the playspace with respect to the edgelength
        and any placed obstacles, and randomly assigns who is It. Returns a list
        of players, and a list of just the players who are not It.
        '''
        try:
            it = r.randrange(0, numPlayers, 1)
            playerIt = r.randrange(1, numPlayers+1, 1)
            players = []
            for i in range (numPlayers):
            playersNotIt = []
            for i in range (1, numPlayers+1):
                # Get a random position a reasonable distance from other players
                # with respect to edge length. Don't use origin, this is dummy code
                x, y, z = (0, 0, 0)                
                if(i == it): it = True
                else: it = False
                if(i == playerIt): it = True
                else:
                    it = False
                    playersNotIt.append(i)
                players.append(Player(i, x, y, z, it))

            return players, playersNotIt
        except:
            print("An error occurred placing players")

    def placeObstacles(self, numObstacles):
        '''
        Randomly places obstacles in the playspace with respect to the edgelength
        and any other obstacles.
        '''
        try:
            print("This will place up to number of obstacles in appropriately",
                    "randomized positions, with respect to edge length")
            # Add obstacle code here
            pass
        except:
            print("An error occurred placing obstacles")

    def placePowerUps(self, numPowerUps):
        '''
        Randomly places powerups in the playspace with respect to the edgelength
        and any other powerups.
        '''
        try:
            print("This will place up to number of powerups in appropriately",
                    "randomized positions, with respect to edge length")
            # Add powerUp code here
            pass
        except:
            print("An error occurred placing powerups")

    def movePlayer(self, player, direction):
    def movePlayer(self, playerId, direction):
        '''
        Takes a player ID and direction and checks if a move is possible.
        '''
        try:
            # First check for collision
            collision, tag, powerup = self.checkCollision(player, direction)
            collision, tag, powerup = self.checkCollision(playerId, direction)
            # If collision is a tag, do the tagging stuff
            # If collision is obstacle/wall/non tag player bump, do nothing
            # Otherwise move. If there's a powerup there, pick it up
            #sender.update("playerID , updated locations")
            #send.send()
            if(tag):
                tag.setIt()
                player.setNotIt()
                if player in self.playersNotIt:
                    self.playersNotIt.remove(player)
                     #sender.update("playerID , updated it var")
                    #send.send()
                self.players[tag - 1].setIt()
                self.players[playerId - 1].setNotIt()
                if tag.PlayerId in self.playersNotIt:
                    self.playersNotIt.remove(tag)

        except:
            print("An error occurred moving player", player, ":", direction)
            print("An error occurred moving player", playerId, ":", direction)

    def rotatePlaySpace(self, player, rotation):
    def rotatePlaySpace(self, rotation):
        '''
        Takes a rotation, rotates the playspace.
        '''
        try:
            print("This will attempt to rotate the playspace")
            # write this
             #sender.update("playerID , updated rotation")
            #send.send()
            pass
        except:
            print("An error occurred rotating", rotation, "from player", player)
            print("An error occurred rotating", rotation)

    def checkCollision(self, player, direction):
        '''
        Takes a player and direction, figures out if they are going to run into 
        stuff.
        
        Return tuple (collision, tag, powerup):
         - collision: bool indicating a collision with obstacle, edge, or
             another player where the moving player is not it
         - tag: if the moving player is it and the obstacle is another
             player, this is the other playerId, else 0
         - powerup: if the obstacle is a powerup, this is the index for it
        '''
        try:
            print("This will check if an obstacle exists where the player wants",
                  "to move")
            # Return tuple (collision, tag, powerup):
            #  - collision: bool indicating a collision with obstacle, edge, or
            #       another player where the moving player is not it
            #  - tag: if the moving player is it and the obstacle is another
            #       player, this is the other player, else 0
            #  - powerup: if the obstacle is a powerup, this is the index for it
            # These are dummy vals
            collision, tag, powerup = (0,0,0)
            return collision, tag, powerup
        except:
            print("An error occurred checking collision")

    def setRotationCoolDown(self):
        '''
        Starts the rotation cooldown
        '''
        try:
            self.rotationCoolDownRemaining = ROTATION_COOLDOWN
        except:
            print("An error occurred setting the rotation cooldown")

    def rotationCoolDown(self):
        '''
        Counts down the rotation cooldown.
        '''
        try:
            if(self.rotationCoolDownRemaining>0): self.rotationCoolDownRemaining -= 1
        except:
            print("An error occurred decrementing the rotation cooldown")
            print("An error occurred decrementing the rotation cooldown")        

class Player:
    def __init__(self, playerNum, x, y, z, it):
    def __init__(self, playerId, x, y, z, it):
        try:
            self.playerNum = playerNum;
            self.playerId = playerId;
            self.x = x
            self.y = y
            self.z = z
@@ -156,6 +208,9 @@ def __init__(self, playerNum, x, y, z, it):
            print("An error occurred initializing Player")

    def setPosition(self, x, y, z):
        '''
        Sets the player position values
        '''
        try:
            self.x = x
            self.y = y
@@ -164,15 +219,22 @@ def setPosition(self, x, y, z):
            print("An error occurred updating player position")

    def setIt(self):
        '''
        Sets the player as It
        '''
        try:
            if(not self.it): self.it = True
            if(not self.it):
                self.it = True
            else: print("Tagged person was already it, something went wrong")
        except:
            print("An error occurred updating who is it")

    def setNotIt(self):
        '''
        Sets the player as Not It
        '''
        try:
            if(self.it): self.it = False
            else: print("Tagged person was already not it, something went wrong")
        except:
            print("An error occurred updating who is it")             
            print("An error occurred updating who is it") 