from flask import Flask, abort, redirect, request, make_response
from flask_negotiation import provides
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, VOID, XSD
from rdflib.plugin import register, Serializer
from itertools import izip_longest
import urllib2, rdflib, math

app = Flask(__name__)

rdflib.plugin.register('application/ld+json', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')
rdflib.plugin.register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')

dataset_uri = "https://wsburroughs.link/"
gh_pages_root_uri = "http://bradleypallen.org/anything-but-routine-ld"
root_relative_uri = "/anything-but-routine/"
root_uri = dataset_uri + root_relative_uri
dump_file_relative_uri = "/anything-but-routine/dump"
well_known_void_uri = "/anything-but-routine/.well-known/void"
resource_relative_uri = "/anything-but-routine/<path:resource>"
tpf_relative_uri = "/anything-but-routine/fragment"

abr = rdflib.Namespace(dataset_uri)
abrc = rdflib.Namespace(dataset_uri + "4.0/classification/")
abri = rdflib.Namespace(dataset_uri + "4.0/instance/")
abrw = rdflib.Namespace(dataset_uri + "4.0/work/")
bf = rdflib.Namespace("http://id.loc.gov/ontologies/bibframe/")
arm = rdflib.Namespace("https://w3id.org/arm/core/ontology/0.1/")
dcterms = rdflib.Namespace("http://purl.org/dc/terms/")
void = rdflib.Namespace("http://rdfs.org/ns/void#")
foaf = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
hydra = rdflib.Namespace("http://www.w3.org/ns/hydra/core#")

def initialize_graph_namespaces(graph):
    graph.bind("abr", dataset_uri)
    graph.bind("abrc", dataset_uri + "4.0/classification/")
    graph.bind("abri", dataset_uri + "4.0/instance/")
    graph.bind("abrw", dataset_uri + "4.0/work/")
    graph.bind("bf", "http://id.loc.gov/ontologies/bibframe/")
    graph.bind("arm", "https://w3id.org/arm/core/ontology/0.1/")
    graph.bind("dcterms", "http://purl.org/dc/terms/")
    graph.bind("void", "http://rdfs.org/ns/void#")
    graph.bind("foaf", "http://xmlns.com/foaf/0.1/")
    graph.bind("hydra", "http://www.w3.org/ns/hydra/core#")
    return graph

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def target_gh_pages_ttl_uri(path=""):
    return "{}/{}.ttl".format(gh_pages_root_uri, path)

dump_graph = initialize_graph_namespaces(Graph().parse(target_gh_pages_ttl_uri("dump"), format="n3"))

void_graph = initialize_graph_namespaces(Graph().parse(target_gh_pages_ttl_uri("void"), format="n3"))

page_size = 100

def emit_accepted_rdf_serialization(graph, media_type):
    if media_type == 'application/rdf+xml':
        response = make_response(graph.serialize(None, format='xml'))
        response.headers['content-type'] = 'application/rdf+xml'
    elif media_type == 'text/plain':
        response = make_response(graph.serialize(None, format='ntriples'))
        response.headers['content-type'] = 'text/plain'
    elif media_type == 'application/ld+json':
        response = make_response(graph.serialize(None, format='json-ld', indent=4))
        response.headers['content-type'] = 'application/ld+json'
    else: # return text/turtle
        response = make_response(graph.serialize(None, format='turtle'))
        response.headers['content-type'] = 'text/turtle'
    return response

@app.route(root_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', 'application/ld+json', to='media_type')
def get_root(media_type):
    if media_type == 'text/html':
        return redirect(gh_pages_root_uri)
    try:
        graph = initialize_graph_namespaces(Graph().parse(target_gh_pages_ttl_uri("void"), format='n3'))
    except urllib2.HTTPError as e:
        abort(e.code)
    return emit_accepted_rdf_serialization(graph, media_type)

@app.route(dump_file_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', 'application/ld+json', to='media_type')
def get_dump(media_type):
#    return redirect(target_gh_pages_ttl_uri("dump"))
    return emit_accepted_rdf_serialization(dump_graph, media_type)

@app.route(well_known_void_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', 'application/ld+json', to='media_type')
def get_well_known_void(media_type):
    return emit_accepted_rdf_serialization(void_graph, media_type)

@app.route(resource_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', 'application/ld+json', to='media_type')
def get_resource(resource, media_type):
    try:
        graph = initialize_graph_namespaces(Graph().parse(target_gh_pages_ttl_uri(resource), format='n3'))
    except urllib2.HTTPError as e:
        abort(e.code)
    return emit_accepted_rdf_serialization(graph, media_type)

@app.route(tpf_relative_uri)
@provides('text/html', 'text/turtle', 'application/rdf+xml', 'text/plain', 'application/x-turtle', 'text/rdf+n3', 'application/ld+json', to='media_type')
def get_tpf(media_type):
    fragment_uri = dataset_uri[:-1] + request.full_path
    s = request.args.get('s')
    if s:
        s = URIRef(s)
    p = request.args.get('p')
    if p:
        p = URIRef(p)
    o = request.args.get('o')
    if o:
        if o.startswith('http'):
            o = URIRef(o)
        else:
            o = Literal(o)
    pg = request.args.get('page')
    if pg:
        pg = int(pg)
    else:
        pg = 0

    data = initialize_graph_namespaces(Graph())
    triples = [ triple for triple in dump_graph.triples( (s, p, o) ) ]
    n_triples = len(triples)
    for i, page in enumerate(grouper(triples, page_size)):
        if i == pg:
            for triple in page:
                if triple:
                    data.add(triple)
            break

    metadata = initialize_graph_namespaces(Graph())
    metadata.add( (URIRef(fragment_uri), VOID.triples, Literal(n_triples, datatype=XSD.integer)) )

    controls = initialize_graph_namespaces(Graph())
    controls.add( (URIRef(dataset_uri), VOID.subset, URIRef(fragment_uri)) )
    controls.add( (URIRef(dataset_uri), hydra.template, Literal("https://wsburroughs.link/anything-but-routine/fragment{?s,p,o}")) )
    s_var = BNode()
    controls.add( (s_var, hydra.variable, Literal("s")) )
    controls.add( (s_var, hydra.property, RDF.subject) )
    p_var = BNode()
    controls.add( (p_var, hydra.variable, Literal("p")) )
    controls.add( (p_var, hydra.property, RDF.predicate) )
    o_var = BNode()
    controls.add( (o_var, hydra.variable, Literal("o")) )
    controls.add( (o_var, hydra.property, RDF.object) )
    controls.add( (URIRef(dataset_uri), hydra.mapping, s_var) )
    controls.add( (URIRef(dataset_uri), hydra.mapping, p_var) )
    controls.add( (URIRef(dataset_uri), hydra.mapping, o_var) )
    controls.add( (URIRef(fragment_uri), RDF.type, hydra.Collection) )
    controls.add( (URIRef(fragment_uri), RDF.type, hydra.PagedCollection) )
    controls.add( (URIRef(fragment_uri), dcterms.title, Literal("Linked Data Fragment of Anything But Routine LD")) )
    controls.add( (URIRef(fragment_uri), dcterms.description, Literal("A Triple Pattern Fragment of the Anything But Routine LD dataset containing triples matching the pattern { ?s ?p ?o }.")) )
    controls.add( (URIRef(fragment_uri), hydra.totalItems, Literal(n_triples, datatype=XSD.integer)) )
    controls.add( (URIRef(fragment_uri), hydra.itemsPerPage, Literal(page_size, datatype=XSD.integer)) )
    if pg >= 1:
        controls.add( (URIRef(fragment_uri), hydra.firstPage, Literal(0, datatype=XSD.integer)) )
    if pg > 1:
        controls.add( (URIRef(fragment_uri), hydra.previousPage, Literal(pg - 1, datatype=XSD.integer)) )
    if pg < math.ceil(n_triples / page_size):
        controls.add( (URIRef(fragment_uri), hydra.nextPage, Literal(pg + 1, datatype=XSD.integer)) )

    graph = data + metadata + controls
    return emit_accepted_rdf_serialization(graph, media_type)
