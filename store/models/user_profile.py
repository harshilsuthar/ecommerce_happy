from django.db import models
from django.contrib.auth.models import User

User._meta.get_field('email')._unique = True
User._meta.get_field('email')._blank = False
User._meta.get_field('email')._null = False

class UserProfile(models.Model):
    """Model definition for UserProfile."""

    # TODO: Define fields here
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    mobile = models.IntegerField()
    image = models.ImageField(upload_to='user_profile', default='user_profile.png')

    class Meta:
        """Meta definition for UserProfile."""

        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfiles'

    def __str__(self):
        return self.user.username