from flask import Flask, abort, make_response
from flask_negotiation import provides
from rdflib import Graph
import urllib2
app = Flask(__name__)

def emit_acceptable_serialization(ttl_uri, media_type):
    try:
        graph = Graph().parse(ttl_uri, format='n3')
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

@app.route('/')
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_void(media_type):
    void_ttl_uri = "http://bradleypallen.org/anything-but-routine-ld/void.ttl"
    return emit_acceptable_serialization(void_ttl_uri, media_type)

@app.route("/<path:entity>")
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_entity(entity, media_type):
    entity_ttl_uri = "http://bradleypallen.org/anything-but-routine-ld{}.ttl".format(entity[entity.rfind('/4.0'):])
    return emit_acceptable_serialization(entity_ttl_uri, media_type)
