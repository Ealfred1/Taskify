from django.db import models
from django.contrib.auth.models import User
from .managers import TaskManager
from cloudinary.models import CloudinaryField


class Category(models.Model):
	name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	class Meta:
	  unique_together = ['name', 'user']
	  verbose_name_plural = 'Categories'
	
	def __str__(self):
	  return str(self.name)


class Task(models.Model):
  PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
  )

  STATUS_CHOICES = (
    ('todo', 'To-Do'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
  )
  
  title = models.CharField(max_length=100)
  description = models.TextField()
  completed = models.BooleanField(default=False)
  due_date = models.DateField()
  priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
  category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
  assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_tasks')
  date_created = models.DateTimeField(auto_now_add=True)

  objects = TaskManager()
	
  def __str__(self):
    return str(self.title)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = CloudinaryField('profile_pics', blank=True, null=True)
    # add user social info and other profile info later!!!

    def __str__(self):
        return self.user.username

User.user_profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])