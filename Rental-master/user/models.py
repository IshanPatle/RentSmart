from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import UserManager


# # Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, name, location, city, state, number, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have a password')
        if not name:
            raise ValueError('User must have a full name')

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.set_password(password)
        user.location = location
        user.city = city
        user.state = state
        user.number = number
        user.admin = is_admin
        user.staff = is_staff
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self,email, name, number, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have a password')
        if not name:
            raise ValueError('User must have a full name')

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.number = number
        user.set_password(password)
        user.admin = True
        user.staff = True
        user.active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):

    email = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=25)
    password = models.CharField(max_length=100)
    location = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    number = models.IntegerField()
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'number']
    objects = UserManager()

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
         return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    user_email = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    address = models.CharField(max_length=200)  
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    dimension = models.CharField(max_length=100)  
    cost = models.IntegerField()
    bedrooms = models.IntegerField()  
    kitchen = models.CharField(max_length=3)  
    hall = models.CharField(max_length=3)  
    balcony = models.CharField(max_length=3)  
    desc = models.CharField(max_length=200)
    AC = models.CharField(max_length=3)  
    img = models.ImageField(upload_to='room_id/', height_field=None, width_field=None, max_length=100)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.room_id)


class Rentals(models.Model):
    rent_id = models.AutoField(primary_key=True)
    user_email = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    item_name = models.CharField(max_length=100)  
    rent_sale = models.CharField(max_length=10)   
    cost = models.DecimalField(max_digits=10, decimal_places=2)  
    location = models.CharField(max_length=100)  
    city = models.CharField(max_length=50)       
    state = models.CharField(max_length=50)   
    year = models.IntegerField()                 
    condition = models.CharField(max_length=50)   
    desc = models.TextField()                    
    img = models.ImageField(upload_to='rent_id/') 
    date = models.DateField(auto_now=True)       

    def __str__(self):
        return self.rent_id 

