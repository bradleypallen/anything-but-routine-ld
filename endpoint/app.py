from flask import Flask, abort, redirect, make_response
from flask_negotiation import provides
from rdflib import Graph
import urllib2
app = Flask(__name__)

gh_pages_root_uri = "http://bradleypallen.org/anything-but-routine-ld"
root_relative_uri = "/anything-but-routine/"
dump_file_relative_uri = "/anything-but-routine/dump"
well_known_void_uri = "/anything-but-routine/.well-known/void"
resource_relative_uri = "/anything-but-routine/<path:resource>"

def emit_accepted_rdf_serialization(ttl_uri, media_type):
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

def target_gh_pages_ttl_uri(path=""):
    return "{}/{}.ttl".format(gh_pages_root_uri, path)

@app.route(root_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_root(media_type):
    if media_type == 'text/html':
        return redirect(gh_pages_root_uri)
    return emit_accepted_rdf_serialization(target_gh_pages_ttl_uri("void"), media_type)

@app.route(dump_file_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_dump(media_type):
    return redirect(target_gh_pages_ttl_uri("dump"))

@app.route(well_known_void_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_well_known_void(media_type):
    return emit_accepted_rdf_serialization(target_gh_pages_ttl_uri("void"), media_type)

@app.route(resource_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', to='media_type')
def get_resource(resource, media_type):
    return emit_accepted_rdf_serialization(target_gh_pages_ttl_uri(resource), media_type)
