#!/usr/bin/env python
"""**web_framework** is an example of building a WebOb and WSGI based
webframework and basic application using a ``pipeline`` to manage the
request / response cycle.

Try it out:

.. code-block:: bash

    # start the server in one shell
    python pipeline/examples/web_framework.py
    # and in another load up the index page anonymously:
    curl http://127.0.0.1:8000/
    # Now login and load the index
    curl -b cookie-jar -c cookie-jar http://user1:pw1@127.0.0.1:8000/
    # Using the same cookie, your session and login should be stored
    curl -b cookie-jar -c cookie-jar http://127.0.0.1:8000/

And, try extending it to improve the session handling, add your favorite
template language support, or create a new page.
"""
from webob import Request, Response, exc
from jinja2 import FileSystemLoader, Environment, select_autoescape

from pipeline import pipeline, Stage

import re
from base64 import b64decode

from gevent import monkey
monkey.patch_all() # noqa


# Application
def index(request, response):
    """ An example view function """
    response.jinja2_template = request.settings.jinja2_env.from_string(
        """{% extends "base.html" %}
        {% block body %}Hello {{ user }}{% endblock %}"""
    )
    user = request.user.username if hasattr(request.user, 'username') else None
    response.context = {'user': user}
    return request, response


class Settings:
    urls = [
        (r'.*', index),
    ]
    basicauth_credentials = [
        ('user1', 'pw1'),
        ('user2', 'pw2'),
    ]
    jinja2_env = Environment(
        loader=FileSystemLoader(['./', './examples/', './pipeline/examples/']),
        autoescape=select_autoescape(['html', 'xml']),
    )


class User:
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, self.username)


# Framework
def expand_args(func):
    """Typical stages handle a single argument. web_framework Stages take both a
    request and response object and return the same. @expand_args takes the
    returned pair and expands that pair into two arguments before calling the
    next stage function.
    """
    def wrapped(args):
        return func(*args)
    return wrapped


def framework(environ, start_response):
    """ framework handles gluing together functions that handle WebOb request
    and response objects.

    This is just a slightly messy example of how stage functions could be
    layered to build a web framework. None of the actual stage implementations
    are complete.
    """
    settings = Settings()

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
                # TODO: parse arguments
                return view_func(request, response)
        raise exc.HTTPNotFound

    @expand_args
    def controller(request, response, **kwargs):
        return request, response

    @expand_args
    def render(request, response):
        if hasattr(response, 'jinja2_template') and hasattr(response, 'context'):
            response.text = response.jinja2_template.render(**response.context)
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
