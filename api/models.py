
from django.db import models
from accounts.models import User

# class User(models.Model):
#     userID = models.AutoField(primary_key=True)
#     imageURI = models.URLField(max_length=200, blank=True)
#     bio = models.TextField(blank=True)

#     def __str__(self):
#         return f'User {self.userID}'

class Balance(models.Model):
    currency = models.CharField(max_length=3)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.amount} {self.currency}'

class Group(models.Model):
    groupID = models.AutoField(primary_key=True)
    users = models.ManyToManyField(User)
    imageURI = models.URLField(max_length=200, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Expense(models.Model):
    expenseID = models.AutoField(primary_key=True)
    isSettled = models.BooleanField(default=False)
    balances = models.ManyToManyField(User, through='UserBalance')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    imageURI = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.title

class UserBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'expense')