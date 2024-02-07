from django.urls import path
from . import views


urlpatterns = [
    path('api/display-create-club/<str:username>/', views.ClubDisplayCreateView.as_view(), name ='displaycreateclub'),
    path('api/display-create-club-players/<str:username>/<str:clubname>/', views.ClubPlayersDisplayCreateView.as_view(), name ='displaycreateclubplayers'),
    path('api/display-create-session/<str:username>/<str:clubname>/', views.SessionDisplayCreateView.as_view(), name ='displaycreatesession'),
    path('api/session-detail/<str:username>/<str:clubname>/<int:year>/<int:month>/<int:day>/', views.SessionDetailView.as_view(), name ='sessiondetail'),
    path('api/add-player-to-session/<str:username>/<str:clubname>/<int:year>/<int:month>/<int:day>/', views.AddPlayerToSessionView.as_view(), name ='addplayertosession'),
    path('api/remove-player-from-session/<str:username>/<str:clubname>/<int:year>/<int:month>/<int:day>/', views.RemovePlayerFromSessionView.as_view(), name ='removeplayerfromsession'),
    path('api/create-match/<str:username>/<str:clubname>/<int:year>/<int:month>/<int:day>/', views.CreateMatchView.as_view(), name ='creatematch'),
    path('api/update-match/<str:username>/<str:clubname>/<int:year>/<int:month>/<int:day>/<int:matchID>/', views.UpdateMatchView.as_view(), name ='updatematch'),
    path('api/fetch-match/<str:username>/<str:clubname>/<int:year>/<int:month>/<int:day>/<int:matchid>/', views.fetchMatchView.as_view(), name ='fetchmatch'),
    path('api/fetch-club-players/<str:username>/<str:clubname>/', views.fetchPlayerDetails.as_view(), name ='fetchclubplayers'),
    path('api/fetch-player-details/<str:username>/<str:clubname>/<str:playername>/', views.fetchSinglePlayerDetails.as_view(), name ='fetchplayerdetails'),
]