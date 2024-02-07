from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from datetime import date
# Create your models here.
def get_today():
    return timezone.now().date()

def get_date_list():
    today = timezone.now().date()
    return [today.strftime('%Y-%m-%d')]


class club(models.Model):
    clubName = models.CharField(max_length = 255)
    clubOrganiser = models.ForeignKey(User,on_delete = models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['clubName', 'clubOrganiser'], name='unique_club')
        ]

    def __str__(self):
        return f"{self.clubName} - Organiser:{self.clubOrganiser.username}"


class player(models.Model):
    playerName = models.CharField(max_length = 255,primary_key = True)
    club = models.ForeignKey(club,on_delete=models.CASCADE)
    win = models.IntegerField(default = 0)
    loss =  models.IntegerField(default = 0)
    inGameFlag = models.BooleanField(default = False)
    elo = models.IntegerField(default = 1200)
    eloHistory = ArrayField(models.IntegerField(),  default=list)
    playhistory = ArrayField(models.CharField(max_length=255), default=list)
    recentlyPlayed = models.BooleanField(default = False)
    
    def __str__(self):
        return str(self.playerName)
    
    def save(self, *args, **kwargs):
        if not self.eloHistory:
            self.eloHistory = [1200]  
        if not self.playhistory:
            self.playhistory = get_date_list()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['playerName', 'club'], name='unique_player')
        ]

class session(models.Model):
    sessionID = models.AutoField(primary_key=True)
    club = models.ForeignKey(club,on_delete=models.CASCADE)
    date = models.DateField(default = get_today)
    players = models.ManyToManyField(player)

    def __str__(self):
        return str(self.date)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sessionID', 'club'], name='unique_session'),
            models.UniqueConstraint(fields=['club', 'date'], name='unique_club_date'),
        ]


class match(models.Model): 
    matchID = models.AutoField(primary_key=True)
    session = models.ForeignKey(session,on_delete=models.CASCADE)
    team1 = models.ManyToManyField(player, related_name='team1', blank=True)
    team2 = models.ManyToManyField(player, related_name='team2', blank=True)
    score = models.CharField(max_length = 255, default = '00-00')
    completed = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['matchID', 'session'], name='unique_match'),
        ]

    def __str__(self):
        team1_names = ", ".join([player.playerName for player in self.team1.all()])
        team2_names = ", ".join([player.playerName for player in self.team2.all()])
        return f"Match: {self.matchID} - Team 1: {team1_names} vs Team 2: {team2_names} - Completed:{self.completed}"
