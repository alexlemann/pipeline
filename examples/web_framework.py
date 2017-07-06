#!/usr/bin/env python
from webob import Request, Response, exc

from pipeline import pipeline, Stage

import re
from base64 import b64decode


class Settings:
    pass

class User:
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, self.username)

# Application
def index(request, response):
    response.write(u'Hello World! {0}\n'.format(request.user))
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

    @expand_args
    def get_session(request, response):
        # request.cookies
        return request, response

    @expand_args
    def basicauth(request, response):
        if request.authorization:
            scheme, credential = request.authorization
            if scheme == 'Basic':
                credential = credential.encode('utf-8')
                login, password = b64decode(credential).decode('utf-8').split(':')
                if (login, password) in settings.basicauth_credentials:
                    request.user = User(login)
        if not hasattr(request, 'user'):
            request.user = None
        return request, response

    @expand_args
    def dispatch(request, response):
        for exp, view_func in settings.urls:
            if re.match(exp, request.path_url):
                # parse arguments
                return view_func(request, response)
        raise exc.Http404

    @expand_args
    def controller(request, response, **kwargs):
        return request, response

    @expand_args
    def render(request, response):
        return request, response

    request = Request(environ)
    response = Response()
    response.write('Pipeline starting\n')

    framework_pipeline = pipeline([
        Stage(get_session),
        Stage(basicauth),
        Stage(dispatch),
        Stage(controller),
        Stage(render)],
        initial_data=[(request, response)])

    framework_pipeline.join()
    request, response = framework_pipeline.values[0]
    response.write('Pipeline finished\n')

    return response(environ, start_response)

if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(framework, host='127.0.0.1', port=8080)
