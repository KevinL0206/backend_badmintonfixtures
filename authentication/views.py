from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import status
from .serializers import UserSerializer
# Create your views here.

class HomeView(APIView):

    permission_classes = (IsAuthenticated, ) # this will make sure that the user is authenticated  
    def get(self, request):       
        content = {'message': 'Welcome to Badminton Fixtures App!'}   
        return Response(content)
    
class LogoutView(APIView):     
    permission_classes = (IsAuthenticated,)     

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token is None:
                return Response({'error': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist() #blacklist the refresh token to prevent future use            
            return Response(status=status.HTTP_205_RESET_CONTENT)          
        except (InvalidToken, TokenError) as e:               
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class UserCreate(APIView):

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)