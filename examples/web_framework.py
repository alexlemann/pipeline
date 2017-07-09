#!/usr/bin/env python
from webob import Request, Response, exc
from webob.cookies import CookieProfile, make_cookie
from jinja2 import FileSystemLoader, Environment, select_autoescape

from pipeline import pipeline, Stage

import re
from base64 import b64decode


# Application
class Settings:
    pass

class User:
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, self.username)

def index(request, response):
    response.jinja2_template = request.settings.jinja2_env.from_string(
        """
        {% extends "base.html" %}
        {% block body %}
        Hello {{ user }}
        {% endblock %}
        """
    )
    response.context = {'user': request.user.username}
    return request, response


# Framework
def expand_args(func):
    def wrapped(args):
        return func(*args)
    return wrapped


def framework(environ, start_response):
    settings = Settings()
    settings.urls = [
        (r'.*', index),
    ]
    settings.basicauth_credentials = [
        ('user1', 'pw1'),
        ('user2', 'pw2'),
    ]
    settings.jinja2_env = Environment(
        loader=FileSystemLoader('./'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    @expand_args
    def attach_settings(request, response):
        request.settings = settings
        return request, response

    @expand_args
    def get_cookies_user(request, response):
        if not hasattr(request, 'user') or request.user is None:
            if 'user' in request.cookies:
                request.user = User(request.cookies['user'])
        if not hasattr(request, 'user'):
            request.user = None
        return request, response

    @expand_args
    def get_basicauth_user(request, response):
        if not hasattr(request, 'user') or request.user is None:
            if request.authorization:
                scheme, credential = request.authorization
                if scheme == 'Basic':
                    credential = credential.encode('utf-8')
                    login, password = b64decode(credential).decode('utf-8').split(':')
                    if (login, password) in settings.basicauth_credentials:
                        request.user = User(login)
                        response.set_cookie('user', login)
        if not hasattr(request, 'user'):
            request.user = None
        return request, response

    @expand_args
    def dispatch(request, response):
        for exp, view_func in settings.urls:
            if re.match(exp, request.path_url):
                # parse arguments
                return view_func(request, response)
        raise exc.HTTPNotFound

    @expand_args
    def controller(request, response, **kwargs):
        return request, response

    @expand_args
    def render(request, response):
        if hasattr(response, 'jinja2_template') and hasattr(response, 'context'):
            response.text = response.jinja2_template.render(**response.context)
            print('yes template')
        return request, response

    request = Request(environ)
    response = Response()

    framework_pipeline = pipeline([
        Stage(attach_settings),
        Stage(get_cookies_user),
        Stage(get_basicauth_user),
        Stage(dispatch),
        Stage(controller),
        Stage(render)],
        initial_data=[(request, response)])

    framework_pipeline.join()
    request, response = framework_pipeline.values[0]

    return response(environ, start_response)

if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(framework, host='127.0.0.1', port=8080)
