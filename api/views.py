from django.shortcuts import render
from django.contrib.auth import authenticate
from .models import Task
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import *
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken



#	This is just a test response

@api_view(['GET'])
def test_response(request):
	response = {
		'Packages': 'package1'
	}
	return Response(response)


# User Registration view
class UserRegistrationView(CreateAPIView):
	serializer_class = UserRegistrationSerializer


# User Login view
class UserLoginView(APIView):
	def post(self, request):
		data = request.data
		serializer = LoginSerializer(data=data)
		
		if serializer.is_valid():
			username = serializer.data['username']
			password = serializer.data['password']
			
			user = authenticate(request,username=username, password=password)
			
			if user is not None:
				refresh = RefreshToken.for_user(user)
				user_serializer = UserRegistrationSerializer(user)
				return Response({
					'refresh': str(refresh),
					'access': str(refresh.access_token),
					#'user': f'{user.first_name} {user.last_name}',
					'user': user_serializer.data
				})
			return Response({
				'message': 'Invalid Credentials'
			})
		
		return Response({
			'message': 'Something went wrong',
			'data': serializer.errors
		})

class TaskList(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)