from rest_framework import serializers
from .models import club,player,session,match
from django.contrib.auth.models import User

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = club
        exclude = ('clubOrganiser',)

class ClubPlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = player
        fields = ('playerName', 'club',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=player.objects.all(),
                fields=('playerName', 'club',)
            )
        ]

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = session
        fields = ('date',)    

class matchSerializer(serializers.ModelSerializer):
    class Meta:
        model = match
        fields = ('matchID','team1','team2','score','completed')
        read_only_fields = ('matchID',)

class SessionPlayersSerializer(serializers.Serializer):
    players = serializers.ListField(child=serializers.CharField())

    def to_internal_value(self, data):
        # Convert player names to player instances
        players = data.get('players')
        if players is not None:
            clubname = self.context['view'].kwargs['clubname']
            username = self.context['view'].kwargs['username']
            userInstance = User.objects.get(username=username)
            clubInstance = club.objects.get(clubName=clubname, clubOrganiser=userInstance)
            player_instances = []
            for player_name in players:
                try:
                    player_instance = player.objects.get(playerName=player_name, club=clubInstance)
                    player_instances.append(player_instance)
                except player.DoesNotExist:
                    raise serializers.ValidationError(f"Player {player_name} does not exist")
            data['players'] = player_instances
        return super().to_internal_value(data)

class UpdateMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = match
        fields = ('score',)

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = player
        fields = ('playerName','win','loss','elo')
        read_only_fields = ('playerName',)

class SinglePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = player
        fields = ('playerName','win','loss','elo','eloHistory','playhistory')
        read_only_fields = ('playerName',)