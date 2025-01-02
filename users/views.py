# from django.shortcuts import render
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status, permissions
from rest_framework.generics import ListAPIView,UpdateAPIView
from rest_framework.response import Response
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Return the user data along with the tokens
        response_data = {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(access),
        }
        return Response(response_data, status=status.HTTP_201_CREATED)



class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user_data = UserSerializer(user).data

        return Response({
            'user': user_data,
            'refresh': str(refresh),
            'access': str(access),
        }, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            # Blacklist the token so it cannot be used again
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)
        


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        print(f"User: {user}") 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data['password']
        print("OLD_PASSWORD =",old_password)
        if not user.check_password(old_password):
            print("THis Password is Valid")
            raise ValidationError({"old_password": "Old password is incorrect."})
        else:
            print("User Password Not Valid")

        new_password = serializer.validated_data['new_password']
        print("New_password =",new_password)
        user.set_password(new_password)
        user.save()

        return Response({"status": True}, status=status.HTTP_200_OK)
    

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get_object(self):
        return self.request.user


