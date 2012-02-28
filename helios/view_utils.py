
"""
Utilities for all views

Ben Adida (12-30-2008)
"""

from django.template import Context, Template, loader
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

import utils

from helios import datatypes

# nicely update the wrapper function
from functools import update_wrapper

from auth.security import get_user

import helios

from django.conf import settings

##
## BASICS
##

SUCCESS = HttpResponse("SUCCESS")

# FIXME: error code
FAILURE = HttpResponse("FAILURE")

##
## template abstraction
##
def prepare_vars(request, vars):
  vars_with_user = vars.copy()
  vars_with_user['user'] = get_user(request)

  # csrf protection
  if request.session.has_key('csrf_token'):
    vars_with_user['csrf_token'] = request.session['csrf_token']

  vars_with_user['STATIC'] = '/static/'
  vars_with_user['MEDIA_URL'] = '/static/'
  vars_with_user['HELIOS_STATIC'] = '/static/helios/helios/'
  vars_with_user['utils'] = utils
  vars_with_user['settings'] = settings
  vars_with_user['TEMPLATE_BASE'] = 'templates/base.html'
  vars_with_user['messages'] = messages.get_messages(request)
  vars_with_user['CURRENT_URL'] = request.path
  vars_with_user['SECURE_URL_HOST'] = settings.SECURE_URL_HOST

  return vars_with_user

def render_template(request, template_name, vars = {}, include_user=True):
  vars_with_user = prepare_vars(request, vars)

  if not include_user:
    del vars_with_user['user']

  return render_to_response('%s.html' % template_name, vars_with_user)

def render_template_raw(request, template_name, vars={}):
  # if there's a request, prep the vars, otherwise can't do it.
  if request:
    full_vars = prepare_vars(request, vars)
  else:
    full_vars = vars

  return render_to_string('%s.html' % template_name, full_vars)


def render_json(json_txt):
  return HttpResponse(json_txt, "application/json")

# decorator
def json(func):
    """
    A decorator that serializes the output to JSON before returning to the
    web client.
    """
    def convert_to_json(self, *args, **kwargs):
      return_val = func(self, *args, **kwargs)
      try:
        return render_json(utils.to_json(return_val))
      except Exception, e:
        import logging
        logging.error(_("problem with serialization: ") + str(return_val) + " / " + str(e))
        raise e

    return update_wrapper(convert_to_json,func)

