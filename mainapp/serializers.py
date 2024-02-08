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
    team1_player_names = serializers.SerializerMethodField()
    team2_player_names = serializers.SerializerMethodField()
    class Meta:
        model = match
        fields = ('matchID','team1','team2','score','completed','team1_player_names', 'team2_player_names')
        read_only_fields = ('matchID',)

    def get_team1_player_names(self, obj):
        return obj.get_team1_player_names()

    def get_team2_player_names(self, obj):
        return obj.get_team2_player_names()

class SessionPlayersSerializer(serializers.Serializer):
    players = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = ('players',)

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