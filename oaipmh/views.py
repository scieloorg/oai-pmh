from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions


def xml_response(body):
    return Response(body=body, charset='utf-8', content_type='application/xml')


@view_config(route_name='root')
def root(request):
    return xml_response(request.repository.identify())

