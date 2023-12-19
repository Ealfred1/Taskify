from django.shortcuts import render
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Task, Category
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
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

class TaskListView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        else:
            return Task.objects.none()
    
    def create(self, request, *args, **kwargs):
      title = request.data.get('title')
      category_id = request.data.get('category')

      default_category = None
      if not category_id:
        try:
          default_category = Category.objects.get(name='Uncategorized', user=request.user)
        except Category.DoesNotExist:
          default_category = Category.objects.create(name='Uncategorized', user=request.user)

      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      
      if default_category:
        serializer.validated_data['category'] = default_category
      self.perform_create(serializer)
      headers = self.get_success_headers(serializer.data)

    # Get the total tasks and count of incomplete tasks for the user
      total_tasks = Task.objects.filter(user=request.user).count()
      incomplete_tasks = Task.objects.filter(user=request.user, completed=False).count()
    
      response_data = {
        'task': serializer.data,
        'total_tasks': total_tasks,
        'incomplete_tasks': incomplete_tasks
      }

      return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class CategoryListView(ListCreateAPIView):
  queryset = Category.objects.all()
  serializer_class = CategorySerializer
  permission_classes = [IsAuthenticated]
  
  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

class CategoryDetailView(RetrieveUpdateDestroyAPIView):
  queryset = Category.objects.all()
  serializer_class = CategorySerializer
  permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

class TaskCompleted(APIView):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.completed = not task.completed
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)