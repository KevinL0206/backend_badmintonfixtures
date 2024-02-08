from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClubSerializer, ClubPlayersSerializer,SessionSerializer,SessionPlayersSerializer,matchSerializer,UpdateMatchSerializer,PlayerSerializer, SinglePlayerSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from .models import club, player,match,session
from rest_framework.permissions import IsAuthenticated
from .functions import calcGameElo
import random
from django.forms.models import model_to_dict

class ClubDisplayCreateView(APIView): # this class will display all the clubs created by the user and also create a new club
    def get(self, request, username, format=None): # this function will return all the clubs created by the user
        user = User.objects.get(username=username)
        clubs = club.objects.filter(clubOrganiser=user)
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)

    def post(self, request, username, format=None): # this function will create a new club
        if not request.user.is_authenticated:
            return Response({'message': 'Unauthorized'}, status=401)
        if request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)
        serializer = ClubSerializer(data=request.data)
        if serializer.is_valid():
            userInstance = User.objects.get(username=username)
            club = serializer.save(clubOrganiser=userInstance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ClubPlayersDisplayCreateView(APIView): # this class will display all the players in a club and also add players to a club

    def get(self, request, username, clubname, format=None):

        currentUser = username
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        players = player.objects.filter(club=clubInstance)
        serializer = ClubPlayersSerializer(players, many=True)
        return Response(serializer.data) 

    def post(self, request, username, clubname, format=None):
        if not request.user.is_authenticated:
            return Response({'message': 'Unauthorized'}, status=401)
        if request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)
        currentUser = username
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)

        # Add club to the request data
        data = request.data.copy()
        data['club'] = clubInstance.id

        serializer = ClubPlayersSerializer(data=data)
        print(serializer.is_valid())
        if serializer.is_valid():
            
            playerInstance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SessionDisplayCreateView(APIView): # this class will display all the sessions in a club and also add sessions to a club

    def get(self,request,username,clubname,format=None):
        currentUser = username
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        sessions = session.objects.filter(club=clubInstance)
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    def post(self,request,username,clubname,format=None):
        if not request.user.is_authenticated:
            return Response({'message': 'Unauthorized'}, status=401)
        if request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)
        serializer = SessionSerializer(data=request.data)

        date = timezone.now()
        currentUser = username
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)

        if session.objects.filter(club = clubInstance,date=date): 
            print("Session already exists")        
            return Response({"detail": "Session already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            sessiondata = serializer.save(club=clubInstance) # create a new session

            clubPlayers = player.objects.filter(club = clubInstance)
            for players in clubPlayers: # set all the players in the club to not in game
                players.inGameFlag = False
                players.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SessionDetailView(APIView): # this class will display all the players and matches in a session

    def get(self,request,username,clubname,year, month, day,format=None):
        currentUser = username
        sessiondate = timezone.datetime(int(year),int(month),int(day))
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)
        matchInstance = match.objects.filter(session=sessionInstance)


        matchserializer = matchSerializer(matchInstance,many=True) # return all the matches in the session
        return Response({
            "matches":matchserializer.data,

        })

class AddPlayerToSessionView(APIView): # this class will add players to a session
    #permission_classes = [IsAuthenticated]

    def get(self,request,username,clubname,year, month, day,format=None): # this function will return all the players in a club who are not in the session

        currentUser = username
        sessiondate = timezone.datetime(int(year),int(month),int(day))
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)
        sessionPlayers = sessionInstance.players.all() # get all the players in the session
        otherPlayers = player.objects.filter(club=clubInstance).exclude(playerid__in=sessionPlayers) # get all the players in the club who are not in the session

        serializer = ClubPlayersSerializer(otherPlayers, many=True)
        return Response(serializer.data)

    def post(self, request, username, clubname, year, month, day, format=None):
        if not request.user.is_authenticated or request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)

        sessiondate = timezone.datetime(int(year), int(month), int(day))
        userInstance = User.objects.get(username=username)
        clubInstance = club.objects.get(clubName=clubname, clubOrganiser=userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)

        for players in request.data['players']:
            try:
                playerInstance = player.objects.get(playerName=players, club=clubInstance)
                sessionInstance.players.add(playerInstance)
            except:
                return Response({"detail": f"Player {players} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Players added to session"}, status=status.HTTP_200_OK)

class RemovePlayerFromSessionView(APIView): # this class will remove players from a session

    def get(self,request,username,clubname,year, month, day,format=None):
        currentUser = username
        sessiondate = timezone.datetime(int(year),int(month),int(day))
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)
        sessionPlayers = sessionInstance.players.all() # get all the players in the session

        serializer = ClubPlayersSerializer(sessionPlayers, many=True)
        return Response(serializer.data)
    
    def post(self,request,username,clubname,year, month, day,format=None):
        if not request.user.is_authenticated or request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)

        sessiondate = timezone.datetime(int(year), int(month), int(day))
        userInstance = User.objects.get(username=username)
        clubInstance = club.objects.get(clubName=clubname, clubOrganiser=userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)

        for players in request.data['players']:
            try:
                playerInstance = player.objects.get(playerName=players, club=clubInstance)
                sessionInstance.players.remove(playerInstance)
            except:
                return Response({"detail": f"Player {players} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Players removed to session"}, status=status.HTTP_200_OK)

class CreateMatchView(APIView): # this class will create a match

    def post(self,request,username,clubname,year, month, day,format=None):
        if not request.user.is_authenticated:
            return Response({'message': 'Unauthorized'}, status=401)
        if request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)
        serializer = matchSerializer(data=request.data)
        print("hi")
        currentUser = username
        sessiondate = timezone.datetime(int(year),int(month),int(day))

        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)
        freePlayers = list(sessionInstance.players.filter(inGameFlag = False).order_by('elo'))

        freeNotPlayed = list(sessionInstance.players.filter(inGameFlag=False, recentlyPlayed=False).order_by('elo'))
        freeHavePlayed = list(sessionInstance.players.filter(inGameFlag=False, recentlyPlayed=True).order_by('elo'))
        
        random_number = random.randint(0,1)

        if len(freePlayers) <4:
            
            return Response({"detail": "Not enough players to create a match"}, status=status.HTTP_400_BAD_REQUEST)
        else:

            if len(freeNotPlayed) >= 4:
                matchPlayers = []
                for _ in range(4):
                    if freeNotPlayed and random_number < 0.5:
                        player = freeNotPlayed.pop()
                        player.inGameFlag = True
                        player.save()
                        matchPlayers.append(player)
                    elif (freeNotPlayed and random_number >= 0.5):
                        player = freeNotPlayed.pop(0)
                        player.inGameFlag = True
                        player.save()
                        matchPlayers.append(player)

                newMatchInstance = match.objects.create(
                    session = sessionInstance,
                    score = '00-00'
                )

                newMatchInstance.team1.add(matchPlayers[0],matchPlayers[3])
                newMatchInstance.team2.add(matchPlayers[1],matchPlayers[2])

                return Response({"detail": "Match created"}, status=status.HTTP_200_OK)
            else:
                matchPlayers = []
                for _ in range(len(freeNotPlayed)):
                    if freeNotPlayed and random_number < 0.5:
                        player = freeNotPlayed.pop()
                        player.inGameFlag = True
                        player.save()
                        matchPlayers.append(player)
                    elif (freeNotPlayed and random_number >= 0.5):
                        player = freeNotPlayed.pop(0)
                        player.inGameFlag = True
                        player.save()
                        matchPlayers.append(player)
                
                for _ in range(4-len(freeNotPlayed)):
                    if freeHavePlayed and random_number < 0.5:
                        player = freeHavePlayed.pop()
                        player.inGameFlag = True
                        player.save()
                        matchPlayers.append(player)
                    elif (freeHavePlayed and random_number >= 0.5):
                        player = freeHavePlayed.pop(0)
                        player.inGameFlag = True
                        player.save()
                        matchPlayers.append(player)

                matchPlayers = sorted(matchPlayers, key=lambda player: player.elo)

                newMatchInstance.team1.add(matchPlayers[0],matchPlayers[3])
                newMatchInstance.team2.add(matchPlayers[1],matchPlayers[2])

                return Response({"detail": "Match created"}, status=status.HTTP_200_OK)

        

class UpdateMatchView(APIView): # this class will update a match

    def post(self,request,username,clubname,year, month, day,matchID,format=None):
        """
        if not request.user.is_authenticated:
            return Response({'message': 'Unauthorized'}, status=401)
        if request.user.username != username:
            return Response({'message': 'Unauthorized'}, status=401)
        """
        serializer = UpdateMatchSerializer(data=request.data)
        currentUser = username
        sessiondate = timezone.datetime(int(year),int(month),int(day))


        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        sessionInstance = session.objects.get(club=clubInstance,date=sessiondate)
        matchInstance = match.objects.get(session=sessionInstance,matchID=matchID)
        players = sessionInstance.players.all()

        if len(list(sessionInstance.players.filter(inGameFlag=False, recentlyPlayed=False))) == len(players):
            for playername in players:
                playername.recentlyPlayed = False

        team1 = matchInstance.team1.all()
        team2 = matchInstance.team2.all()
        team1_ids = [players.playerid for players in team1]
        team2_ids = [players.playerid for players in team2]
        print("team1",team1_ids)
        
        playerOneInstance = player.objects.get(playerid = team1_ids[0])
        playerTwoInstance = player.objects.get(playerid = team1_ids[1])
        playerThreeInstance = player.objects.get(playerid = team2_ids[0])
        playerFourInstance = player.objects.get(playerid = team2_ids[1])    


        if serializer.is_valid() and not matchInstance.completed:
            score = serializer.validated_data['score']
            
            #Get Match Score
            team1Score, team2Score = map(int, score.split('-'))
            
            if team1Score > 21  and team2Score < team1Score - 2 or team2Score > 21 and team1Score < team2Score - 2:
                return Response({"detail": "Invalid score"}, status=status.HTTP_400_BAD_REQUEST)
            if team1Score < 0 or team2Score < 0:
                return Response({"detail": "Invalid score"}, status=status.HTTP_400_BAD_REQUEST)
            if team1Score < 20 and team2Score != 21 or team2Score < 20 and team1Score != 21:
                return Response({"detail": "Invalid score"}, status=status.HTTP_400_BAD_REQUEST)
            #Calculate which team won
            winloss = []
            if team1Score > team2Score:
                winloss = [1,0]
                playerOneInstance.win += 1
                playerTwoInstance.win += 1
                playerThreeInstance.loss += 1
                playerFourInstance.loss += 1
            elif team2Score > team1Score:
                winloss = [0,1]
                playerOneInstance.loss += 1
                playerTwoInstance.loss += 1
                playerThreeInstance.win += 1
                playerFourInstance.win += 1

            matchInstance.score = score
            matchInstance.completed = True
            matchInstance.save()

            #Calculate new ELO rating for each player
            playerOneNewElo,playerTwoNewElo,playerThreeNewElo,playerFourNewElo = calcGameElo(team1,team2,winloss)

            #Update player ELO
            playerOneInstance.elo = playerOneNewElo
            playerOneInstance.eloHistory.append(playerOneNewElo)
            playerOneInstance.playhistory.append(sessiondate.strftime("%Y-%m-%d"))
            playerOneInstance.inGameFlag = False
            playerOneInstance.recentlyPlayed = True
            playerOneInstance.save()

            playerTwoInstance.elo = playerTwoNewElo
            playerTwoInstance.eloHistory.append(playerTwoNewElo)
            playerTwoInstance.playhistory.append(sessiondate.strftime("%Y-%m-%d"))
            playerTwoInstance.inGameFlag = False
            playerTwoInstance.recentlyPlayed = True
            playerTwoInstance.save()

            playerThreeInstance.elo = playerThreeNewElo
            playerThreeInstance.eloHistory.append(playerThreeNewElo)
            playerThreeInstance.playhistory.append(sessiondate.strftime("%Y-%m-%d"))
            playerThreeInstance.inGameFlag = False
            playerThreeInstance.recentlyPlayed = True
            playerThreeInstance.save()

            playerFourInstance.elo = playerFourNewElo
            playerFourInstance.eloHistory.append(playerFourNewElo)
            playerFourInstance.playhistory.append(sessiondate.strftime("%Y-%m-%d"))
            playerFourInstance.inGameFlag = False
            playerFourInstance.recentlyPlayed = True
            playerFourInstance.save()

            return Response({"detail": "Match updated"}, status=status.HTTP_200_OK)
        else:
            if matchInstance.completed:
                return Response({"detail": "Match already completed"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class fetchMatchView(APIView):

    def get(self,request,username,clubname,year, month, day,matchid,format=None):

        matchInstance = match.objects.get(matchID=matchid)
        serializer = matchSerializer(matchInstance)

        return Response(serializer.data)


class fetchPlayerDetails(APIView):
    
    def get(self,request,username,clubname,format=None):
        currentUser = username
        userInstance = User.objects.get(username = currentUser)
        print(userInstance)
        print(clubname)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        players = player.objects.filter(club=clubInstance)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
class fetchSinglePlayerDetails(APIView):
    
    def get(self,request,username,clubname,playername,format=None):
        currentUser = username
        userInstance = User.objects.get(username = currentUser)
        clubInstance = club.objects.get(clubName = clubname,clubOrganiser = userInstance)
        playerInstance = player.objects.get(playerName = playername,club = clubInstance)
        serializer = SinglePlayerSerializer(playerInstance)
        return Response(serializer.data)