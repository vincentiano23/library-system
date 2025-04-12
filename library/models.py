from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, default='')
    registration_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, default='')
    

    def __str__(self):
        return self.registration_number

class Visit(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  
    visit_time = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.student.registration_number} - {self.visit_time}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True) 

    def __str__(self):
        return self.email
