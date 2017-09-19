import time
import logging
import functools
from urllib import parse

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions

from oaipmh import repository


LOGGER = logging.getLogger(__name__)


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


def log_service_time(func):
    """Loga o tempo para o serviço da requisição. Nenhuma exceção relacionada
    a medição deve causar erro no serviço da requisição.
    """
    @functools.wraps(func)
    def wrapper(req):
        start_time = time.time()
        result = func(req)
        elapsed_time = time.time() - start_time
        try:
            LOGGER.info('total time to service the request "%s %s", with body '
                        '"%s": %s ms', req.method, req.url, req.body.decode(req.charset),
                            (elapsed_time * 1000))
        except Exception as exc:
            LOGGER.exception(exc)
        return result
    return wrapper


@view_config(route_name='root')
@log_service_time
def root(request):
    if request.method not in ['GET', 'POST']:
        raise httpexceptions.HTTPMethodNotAllowed()

    body = request.repository.handle_request(query_string(request))
    return xml_response(body)

