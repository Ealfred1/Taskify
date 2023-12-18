from django.db import models
from django.contrib.auth.models import User


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
    ('High', 'High'),
  )
  
  title = models.CharField(max_length=100)
  description = models.TextField()
  completed = models.BooleanField(default=False)
  due_date = models.DateField()
  priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
  category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
  date_created = models.DateTimeField(auto_now_add=True)
	
  def __str__(self):
    return str(self.title)