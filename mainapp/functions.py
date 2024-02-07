from .models import *

def calcGameElo(team1,team2,winloss):
    team1Names = [player.playerName for player in team1.all()]
    team2Names = [player.playerName for player in team2.all()]

    #Player Names
    playerOneName = team1Names[0]
    playerTwoName = team1Names[1]
    playerThreeName = team2Names[0]
    playerFourName = team2Names[1]

    #Player Instance
    playerOne = player.objects.get(playerName = playerOneName)
    playerTwo = player.objects.get(playerName = playerTwoName)
    playerThree = player.objects.get(playerName = playerThreeName)
    playerFour = player.objects.get(playerName = playerFourName)

    #Player ELO rating
    playerOneElo = playerOne.elo
    playerTwoElo = playerTwo.elo
    playerThreeElo = playerThree.elo
    playerFourElo = playerFour.elo

    team1Average = (playerOneElo + playerTwoElo) / 2
    team2Average = (playerThreeElo + playerFourElo) / 2

    expectedOutcomeTeam1 = 1 /(1 + 10**((team2Average - team1Average)/400))
    expectedOutcomeTeam2 = 1 /(1 + 10**((team1Average - team2Average)/400))

    if winloss[0] == 1: # If Team 1 Won
        team1Outcome = 1 
        team2Outcome = 0
    else:
        team1Outcome = 0 
        team2Outcome = 1

    def calcK(elo):
        if elo < 2400:
            k = 20
        else:
            k = 10
        
        return k
    
    playerOneK = calcK(playerOneElo)
    playerTwoK = calcK(playerTwoElo)
    playerThreeK = calcK(playerThreeElo)
    playerFourK = calcK(playerFourElo)

    #New Ratings 
    playerOneNewElo = playerOneElo + playerOneK * (team1Outcome - expectedOutcomeTeam1)
    playerTwoNewElo = playerTwoElo + playerTwoK * (team1Outcome - expectedOutcomeTeam1)
    playerThreeNewElo = playerThreeElo + playerThreeK * (team2Outcome - expectedOutcomeTeam2)
    playerFourNewElo = playerFourElo + playerFourK * (team2Outcome - expectedOutcomeTeam2)

    return playerOneNewElo,playerTwoNewElo,playerThreeNewElo,playerFourNewElo


