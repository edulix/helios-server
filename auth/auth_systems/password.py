"""
Username/Password Authentication
"""

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from auth.models import User
import logging
from ..forms import RegisterForm
from helios.view_utils import *
from helios.utils import random_string

# some parameters to indicate that status updating is possible
STATUS_UPDATES = False


def create_user(username, password, name = None):
  from auth.models import User

  user = User.objects.filter(user_type = 'password', user_id = username)
  if user:
    raise Exception('user exists')
  
  info = {'password' : password, 'name': name}
  user = User.update_or_create(user_type='password', user_id=username, info = info)
  user.save()

class LoginForm(forms.Form):
  username = forms.CharField(max_length=50)
  password = forms.CharField(widget=forms.PasswordInput(), max_length=100)

def password_check(user, password):
  return (user and user.info['password'] == password)
  
# the view for logging in
def password_login_view(request):
  from auth.views import after
  from auth.models import User

  error = None


  if request.method == "GET":
    form = LoginForm()
  else:
    form = LoginForm(request.POST)

    # set this in case we came here straight from the multi-login chooser
    # and thus did not have a chance to hit the "start/password" URL
    request.session['auth_system_name'] = 'password'
    if request.POST.has_key('return_url'):
      request.session['auth_return_url'] = request.POST.get('return_url')

    if form.is_valid():
      username = form.cleaned_data['username'].strip()
      password = form.cleaned_data['password'].strip()
      try:
        user = User.get_by_type_and_id('password', username)
        if password_check(user, password):
          request.session['password_user'] = user
          return HttpResponseRedirect(reverse(after))
      except User.DoesNotExist:
        pass
      error = 'Bad Username or Password'
  
  return render_template(request, 'password/login', {'form': form, 'error': error})
    
def password_forgotten_view(request):
  """
  forgotten password view and submit.
  includes return_url
  """
  from auth.models import User

  if request.method == "GET":
    return render_template(request, 'password/forgot', {'return_url': request.GET.get('return_url', '')})
  else:
    username = request.POST['username']
    return_url = request.POST['return_url']
    
    try:
      user = User.get_by_type_and_id('password', username)
    except User.DoesNotExist:
      return render_template(request, 'password/forgot', {'return_url': request.GET.get('return_url', ''), 'error': 'no such username'})
    
    body = _("""

This is a password reminder:

Your username: %(username)s
Your password: %(password)s

--
%(site_title)s
""") % dict(username=user.user_id, password=user.info['password'], site_title=settings.SITE_TITLE)

    # FIXME: make this a task
    send_mail('password reminder', body, settings.SERVER_EMAIL, ["%s <%s>" % (user.info['name'], user.info['email'])], fail_silently=False)
    
    return HttpResponseRedirect(return_url)
  
def get_auth_url(request, redirect_url = None):
  return reverse(password_login_view)
    
def get_user_info_after_auth(request):
  user = request.session['password_user']
  del request.session['password_user']
  user_info = user.info
  
  return {'type': 'password', 'user_id' : user.user_id, 'name': user.name, 'info': user.info, 'token': None}
    
def update_status(token, message):
  pass
  
def send_message(user_id, user_name, user_info, subject, body):
  email = user_id
  name = user_name or user_info.get('name', email)
  send_mail(subject, body, settings.SERVER_EMAIL, ["%s <%s>" % (name, email)], fail_silently=False)    


def password_register(request):
  '''
  Registers an user, sending him an email with his new password, therefore
  checking that he entered the correct email.
  '''
  error = None

  if 'password' not in settings.AUTH_ENABLED_AUTH_SYSTEMS:
    return redirect('/')

  if request.method == "GET":
    form = RegisterForm()
  else:
    form = RegisterForm(request.POST)
    if not form.is_valid():
      error = _("Please fix the errors in the form.")
    elif User.objects.filter(user_id=request.POST['email']).exists():
      error = _("An user with the given email address is already registered.")
    else:
      try:
        new_user = User.objects.create(user_type='password',user_id=request.POST['email'],
          name=request.POST['name'], info={'name':request.POST['name'],
          'email':request.POST['email'],'password': random_string(10)})
      except:
        error = _("User already exists.")
        return render_template(request, 'password/register', {'form': form, 'error': error})
      new_user.save()

      mail_body = _("""

Hi %(username)s, you just registered into %(site_title)s. Here are your login details:

Your username: %(userid)s
Your password: %(password)s

--
%(site_title)s
""") % dict(usernmae=new_user.info['name'], site_title=settings.SITE_TITLE, userid=new_user.user_id, password=new_user.info['password'])
      mail_title = _("Welcome to %(site_title)s, %(username)s") % dict(site_title=settings.SITE_TITLE, username=new_user.info['name'])

      send_mail(mail_title, mail_body, settings.SERVER_EMAIL, ["%s <%s>" % (new_user.info['name'], new_user.info['email'])], fail_silently=False)


      messages.add_message(request, messages.SUCCESS, _('You have just been registered in %s. Check your email for your login details.') % settings.SITE_TITLE)

      return redirect('/')

  return render_template(request, 'password/register', {'form': form, 'error': error})
