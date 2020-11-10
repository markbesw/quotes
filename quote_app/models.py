from django.db import models
import re

# Create your models here.

class UserManager(models.Manager):
    def validate(self, postdata):
        email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        if len(postdata['f_n']) < 2:
            errors['f_n'] = "First name must be 2 or more characters"
        if len(postdata['l_n']) < 2:
            errors['l_n'] = "Last name must be 2 or more characters"
        if len(postdata['pw']) < 8:
            errors['pw'] = "Password must be at least 8 characters"
        if postdata['pw'] != postdata['conf_pw']:
            errors['conf_pw'] = "Password does not match confirm password"
        # email check
        if len(postdata['email']) == 0:
            errors['no_email'] = "Please supply an email address"
        else:
            if not email_check.match(postdata['email']):
                errors['email'] = "Invalid email address"
            # check for email already in use (if email is empty, skip the check, else get a DB validator error)
            qs = User.objects.filter(email=postdata['email'])
            if qs:
                errors['email in use'] = f"Email address {postdata['email']} is already in use."
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    # quotes = list of Quote objects (foreign key)

class QuoteMgr(models.Manager):
    def validate(self, postdata):
        errors = {}
        if len(postdata['content']) < 10:
            errors['content'] = "Your quote must have at least 10 characters."
        if len(postdata['quoter']) < 3:
            errors['quoter'] = "Quote author must have at least 3 characters."
        return errors

class Quote(models.Model):
    content = models.TextField()
    quoter = models.CharField(max_length=100)
    poster = models.ForeignKey(User, related_name="quotes", on_delete = models.CASCADE)
    likes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuoteMgr()
