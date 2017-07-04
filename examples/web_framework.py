#!/usr/bin/env python
from webob import Request, Response, exc

from pipeline import pipeline, Stage

import re


# Application
def index(request, response):
    response.write('Hello World!\n')
    return request, response

urls = [
    (r'.*', index),
]


# Framework
def expand_args(func):
    def wrapped(args):
        return func(*args)
    return wrapped


def framework(environ, start_response):

    @expand_args
    def get_session(request, response):
        # request.cookies
        return request, response

    @expand_args
    def dispatch(request, response):
        for exp, view_func in urls:
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
