from urllib import parse

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions

from oaipmh import repository


def xml_response(body):
    return Response(body=body, charset='utf-8', content_type='text/xml')


def query_string(request):
    if request.method == 'GET':
        return request.query_string
    elif request.method == 'POST':
        # a querystring obtida de request.POST já foi devidamente 
        # decodificada pelo framework, por isso é utilizada ao invés de
        # request.body
        return parse.urlencode(request.POST)
    else:
        raise ValueError('Cannot get querystring from request: "%s"' % request)


@view_config(route_name='root')
def root(request):
    if request.method not in ['GET', 'POST']:
        raise httpexceptions.HTTPMethodNotAllowed()

    body = request.repository.handle_request(query_string(request))
    return xml_response(body)

