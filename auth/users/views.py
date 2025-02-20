from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password or not email:
        return Response({'error': 'Fill the required fields'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        access_token = AccessToken.for_user(user)
        return Response({
            'access_token': str(access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
    })
    
@api_view(['GET'])
def login_status(request):
    if request.user.is_authenticated:
        return Response({'status': 'Logged In', 'user': {'id': request.user.id, 'username': request.user.username}}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'Not Logged In'}, status=status.HTTP_401_UNAUTHORIZED)
