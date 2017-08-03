from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions


@view_config(route_name='root', renderer='string')
def root(request):
    return request.repository.identify().decode('utf-8')

