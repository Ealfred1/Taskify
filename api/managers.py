from django.db import models

class TaskManager(models.Manager):
    def overdue_tasks(self, user):
        return self.filter(user=user, due_date__lt=models.DateTimeField.now(), completed=False)
