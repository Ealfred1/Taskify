from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
	title = models.CharField(max_length=100)
	description = models.TextField()
	due_date = models.DateField()
	priority = models.CharField(max_length=20, default='Medium')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
	date_created = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return str(self.title)