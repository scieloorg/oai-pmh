from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions

from oaipmh import repository


def xml_response(body):
    return Response(body=body, charset='utf-8', content_type='text/xml')


@view_config(route_name='root')
def root(request):
    body = request.repository.handle_request(request.query_string)
    return xml_response(body)

