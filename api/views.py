from django.shortcuts import render
from django.db.models import Count
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Task, Category, UserProfile
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
  user_instance = User.objects.get(username='Eric')
  user_profile = user_instance.user_profile
  print(user_profile.bio)
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
			return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
		
		return Response({
			'message': 'Something went wrong',
			'data': serializer.errors
		})

class DashboardView(APIView):
  permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

  def get(self, request, *args, **kwargs):
    # Retrieve categories with task counts
    categories = Category.objects.filter(user=request.user).annotate(task_count=Count('task'))
    categories_serialized = CategorySerializer(categories, many=True)

    # Retrieve recent tasks
    recent_tasks = Task.objects.filter(user=request.user).order_by('-date_created')[:4]
    recent_tasks_serialized = TaskSerializer(recent_tasks, many=True)

    # Get counts of completed and pending tasks
    completed_tasks_count = Task.objects.filter(user=request.user, completed=True).count()
    pending_tasks_count = Task.objects.filter(user=request.user, completed=False).count()
    task_in_progress = Task.objects.filter(user=request.user, status="in_progress").count()
    task_todo = Task.objects.filter(user=request.user, status="todo").count()


    # Prepare summary statistics
    summary_stats = {
        'total_categories': categories.count(),
        'categories': categories_serialized.data,
        'recent_tasks': recent_tasks_serialized.data,
        'completed_tasks': completed_tasks_count,
        'pending_tasks': pending_tasks_count,
        'task_todo': task_todo,
        'task_in_progress': task_in_progress
    }

    return Response(summary_stats, status=status.HTTP_200_OK)

class TaskListView(ListCreateAPIView):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    if self.request.user.is_authenticated:
      return Task.objects.filter(user=self.request.user).order_by("due_date")
    else:
      return Task.objects.none()

  def create(self, request, *args, **kwargs):
    category_id = request.data.get('category')

    if category_id:
      category = Category.objects.get(name=category_id, user=request.user)
      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save(user=request.user, category=category)
    else:
      default_category, created = Category.objects.get_or_create(name='Uncategorized', user=request.user)
      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save(user=request.user, category=default_category)

    headers = self.get_success_headers(serializer.data)

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

  def get_queryset(self):
    if self.request.user.is_authenticated:
      return Category.objects.filter(user=self.request.user)
    else:
      return Category.objects.none()
  
  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

class CategoryDetailView(RetrieveUpdateDestroyAPIView):
  queryset = Category.objects.all()
  serializer_class = CategorySerializer
  permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

  def get_serializer_context(self):
    context = super().get_serializer_context()
    context.update({'request': self.request})
    return context

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    tasks = instance.task_set.all()  # Get tasks related to this category
    tasks_serializer = TaskSerializer(tasks, many=True)

    serialized_data = self.get_serializer(instance).data
    serialized_data['task_count'] = tasks.count()
    serialized_data['tasks'] = tasks_serializer.data

    return Response(serialized_data)

class TaskCompleted(APIView):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.completed = not task.completed
        task.status = 'completed' if task.completed else 'in_progress'
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileCreateView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    request.data['user'] = request.user.id

    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileDetailSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
