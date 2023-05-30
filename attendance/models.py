from django.db import models


class AttendanceLog(models.Model):
    user = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.status}"


class RegisteredUser(models.Model):
    name = models.CharField(max_length=100,unique=True)
    image=models.ImageField()
    embeddings = models.BinaryField()

    def __str__(self):
        return self.name
