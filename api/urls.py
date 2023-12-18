from django.urls import path
from .views import *

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
	path('', test_response),
	path('register/', UserRegistrationView.as_view()),
	path('login/', UserLoginView.as_view()),
  path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  
  path('tasks/', TaskListView.as_view()),
  path('tasks/<int:pk>', TaskDetailView.as_view()),
  path('categories/', CategoryListView.as_view()),
]