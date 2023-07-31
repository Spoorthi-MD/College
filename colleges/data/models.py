from django.db import models


# Create your models here.

class Colleges(models.Model):
    college_code = models.IntegerField()
    college_name = models.CharField(max_length=100)

    def __str__(self):
        return self.college_name


class Branches(models.Model):
    branch_code = models.IntegerField()
    branch_name = models.CharField(max_length=100)

    def __str__(self):
        return self.branch_name


class Streams(models.Model):
    college = models.ForeignKey(Colleges, on_delete=models.CASCADE, related_name='streams')
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='streams')

    def __str__(self):
        return f"{self.college.college_name} - {self.branch.branch_name}"


class Students(models.Model):
    reg_num = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    b_name = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='students')
    c_name = models.ForeignKey(Colleges, on_delete=models.CASCADE, related_name='students')

    def __str__(self):
        return self.first_name



