from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions

from oaipmh import repository, entities


def xml_response(body):
    return Response(body=body, charset='utf-8', content_type='application/xml')


def oairequest_from_http(request):
    oairequest = entities.OAIRequest(
            verb=request.params.get('verb'),
            identifier=request.params.get('identifier'),
            metadataPrefix=request.params.get('metadataPrefix'),
            set=request.params.get('set'),
            resumptionToken=request.params.get('resumptionToken'),
            from_=request.params.get('from'),
            until=request.params.get('until'),
            )
    return oairequest


@view_config(route_name='root')
def root(request):
    oairequest = oairequest_from_http(request)
    body = request.repository.handle_request(oairequest)
    return xml_response(body)

