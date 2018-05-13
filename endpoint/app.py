from flask import Flask, abort, make_response
from flask_negotiation import provides
from rdflib import Graph
import urllib2
app = Flask(__name__)

@app.route("/<path:entity>")
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_entity(entity, media_type):
    gh_pages_ttl = "http://bradleypallen.org/{}.ttl".format(entity)
    try:
        graph = Graph().parse(gh_pages_ttl, format='n3')
    except urllib2.HTTPError as e:
        abort(e.code)
    if media_type == 'application/rdf+xml':
        response = make_response(graph.serialize(None, format='xml'))
        response.headers['content-type'] = 'application/rdf+xml'
    elif media_type == 'text/plain':
        response = make_response(graph.serialize(None, format='ntriples'))
        response.headers['content-type'] = 'text/plain'
    else: # return text/turtle
        response = make_response(graph.serialize(None, format='turtle'))
        response.headers['content-type'] = 'text/turtle'
    return response
