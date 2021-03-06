import rdflib, glob, datetime, time, pandas as pd
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, VOID, DCTERMS, XSD

class ABRBibliography():

    def __init__(self, ttl='docs/4.0/*/*.ttl'):
        self.ld_path_prefix = "https://wsburroughs.link/anything-but-routine/"
        self.abr = rdflib.Namespace(self.ld_path_prefix)
        self.abrc = rdflib.Namespace(self.ld_path_prefix + "4.0/classification/")
        self.abri = rdflib.Namespace(self.ld_path_prefix + "4.0/instance/")
        self.abrw = rdflib.Namespace(self.ld_path_prefix + "4.0/work/")
        self.bf = rdflib.Namespace("http://id.loc.gov/ontologies/bibframe/")
        self.arm = rdflib.Namespace("https://w3id.org/arm/core/ontology/0.1/")
        self.dcterms = rdflib.Namespace("http://purl.org/dc/terms/")
        self.void = rdflib.Namespace("http://rdfs.org/ns/void#")
        self.foaf = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
        self.hydra = rdflib.Namespace("http://www.w3.org/ns/hydra/core#")
        self.terminating_chars = ['!', '?', '.']
        self.graph = rdflib.Graph()
        self.initialize_graph_namespaces(self.graph)
        for infile in glob.glob(ttl):
            self.graph.parse(infile, format='n3')

    def initialize_graph_namespaces(self, graph):
        graph.bind("abr", self.ld_path_prefix)
        graph.bind("abrc", self.ld_path_prefix + "4.0/classification/")
        graph.bind("abri", self.ld_path_prefix + "4.0/instance/")
        graph.bind("abrw", self.ld_path_prefix + "4.0/work/")
        graph.bind("bf", "http://id.loc.gov/ontologies/bibframe/")
        graph.bind("arm", "https://w3id.org/arm/core/ontology/0.1/")
        graph.bind("dcterms", "http://purl.org/dc/terms/")
        graph.bind("void", "http://rdfs.org/ns/void#")
        graph.bind("foaf", "http://xmlns.com/foaf/0.1/")
        graph.bind("hydra", "http://www.w3.org/ns/hydra/core#")

    def instance_entry(self, instance):
        entry = ''
        # bf:classification
        category = self.graph.value(instance, self.bf.classification)
        # bf:identifiedBy
        ids = {}
        for id in self.graph.objects(instance, self.bf.identifiedBy):
            ids['{}'.format(self.graph.value(id, self.bf.source))] = [ id_str for id_str in self.graph.objects(id, RDF.value) ]
        # Schottlaender no. + bf:title
        schottlaender_id = ids['Schottlaender v4.0'][0]
        # titles can be more complex
        title = self.graph.value(self.graph.value(instance, self.bf.title), RDFS.label) or self.graph.value(instance, RDFS.label)
        if title[-1] in self.terminating_chars:
            entry += '{}. _{}_ '.format(schottlaender_id, title)
        else:
            entry += '{}. _{}._ '.format(schottlaender_id, title)
        # bf:contributor
        entry += "{}. ".format('; '.join([ '{}, {}'.format(self.graph.value(contributor, RDFS.label), ', '.join([ role for role in self.graph.objects(contributor, self.bf.role) ])) for contributor in self.graph.objects(instance, self.bf.contributor) ]))
        # bf:provisionActivity
        if category not in [ self.abrc['C'] ]:
            entry += "{}. ".format('; '.join([ '{}: {}, {}'.format(self.graph.value(publisher, self.bf.place), self.graph.value(publisher, self.bf.agent), self.graph.value(publisher, self.bf.date)) for publisher in self.graph.objects(instance, self.bf.provisionActivity) ]))
        # bf:copyrightDate
        if self.graph.value(instance, self.bf.copyrightDate):
            entry += '©{}. '.format(self.graph.value(instance, self.bf.copyrightDate))
        # dcterms:hasPart
        binding = self.graph.value(instance, self.dcterms.hasPart)
        if binding:
            descriptive_note = self.graph.value(binding, self.bf.note)
            entry += '{} '.format(self.graph.value(descriptive_note, RDF.value))
        # M&M no. (if present)
        if 'Maynard & Miles' in ids:
            entry += '{M&M ' + ', '.join(ids['Maynard & Miles']) + '}'
        # Link to .ttl
        entry += ' _[ttl]({})_'.format(instance)
        return entry

    def to_records(self):
        qres = self.graph.query(
            """SELECT DISTINCT ?w ?title ?c ?cl ?abrno ?date ?i
               WHERE {
                  ?w rdf:type bf:Work .
                  ?w rdfs:label ?title .
                  ?w bf:classification ?c .
                  ?c rdfs:label ?cl .
                  ?i bf:instanceOf ?w .
                  ?i bf:identifiedBy ?id .
                  ?id bf:source 'Schottlaender v4.0' .
                  ?id rdf:value ?abrno .
                  ?i bf:provisionActivity ?pa .
                  ?pa bf:date ?date .
               }
               ORDER BY ASC(?date)""")
        results = [ [ row[i].toPython() for i in range(len(row)) ] for row in qres ]
        instance_df = pd.DataFrame(results, columns=['work', 'worktitle', 'category', 'catlabel', 'id', 'date', 'instance'])
        instance_df['workid'] = instance_df['work'].apply(lambda x: x[x.rfind('/')+1:])
        instance_df['workidsort'] = instance_df['workid'].apply(lambda x: x[0] + x[1:].rjust(5, '0'))
        instance_df['category'] = instance_df['category'].str[-1]
        instance_df['year'] = instance_df['date'].str.extract('\[?(\d\d\d\d)', expand=False)
        instance_df = instance_df.sort_values(by=['workidsort', 'id'])
        instance_df = instance_df[['year', 'workid', 'category', 'catlabel', 'worktitle', 'id', 'instance']]
        return instance_df.to_dict('records')

    def generate_documentation(self, file='docs/index.md'):
        with open(file, 'w') as mdfile:
            current_category = None
            current_work = None
            current_year = '0000'
            for i in self.to_records():
                instance = URIRef(i['instance'])
                if i['category'] != current_category:
                    current_category = i['category']
                    current_year = '0000'
                    print(f"# {current_category}. {i['catlabel']}", file=mdfile)
                    print('', file=mdfile)
                if i['workid'] != current_work:
                    if i['year'] > current_year:
                        current_year = i['year']
                        print(f"## {current_year}", file=mdfile)
                        print('', file=mdfile)
                    current_work = i['workid']
                    if i['workid'] != i['id']:
                        if i['worktitle'][-1] in self.terminating_chars:
                            print(f"### {current_work}. _{i['worktitle']}_", file=mdfile)
                            print('', file=mdfile)
                        else:
                            print(f"### {current_work}. _{i['worktitle']}._", file=mdfile)
                            print('', file=mdfile)
                if i['workid'] != i['id']:
                    print('#### {}'.format(self.instance_entry(instance)), file=mdfile)
                else:
                    print('### {}'.format(self.instance_entry(instance)), file=mdfile)
                print('', file=mdfile)
                # bf:note
                for note in self.graph.objects(instance, self.bf.note):
                    print('- {}'.format(self.graph.value(note, RDF.value)), file=mdfile)
                print('', file=mdfile)
                # bf:relatedTo (if present)
                if self.graph.value(instance, self.bf.relatedTo):
                    print('#### Related entities', file=mdfile)
                    print('', file=mdfile)
                    for related in self.graph.objects(instance, self.bf.relatedTo):
                        print('##### {}'.format(self.instance_entry(related)), file=mdfile)
                        print('', file=mdfile)
                        for note in self.graph.objects(related, self.bf.note):
                            print('- {}'.format(self.graph.value(note, RDF.value)), file=mdfile)
                        print('', file=mdfile)

    def update_void_description(self):
        void_file = 'docs/void.ttl'
        h = rdflib.Graph()
        self.initialize_graph_namespaces(h)
        h.parse(void_file, format='n3')
        # dcterms:modified
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        now = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
        h.remove( (self.abr[''], self.dcterms.modified, None) )
        h.add( (self.abr[''], self.dcterms.modified, Literal(now, datatype=XSD.dateTime)) )
        # void:triples
        h.remove( (self.abr[''], self.void.triples, None) )
        h.add( (self.abr[''], self.void.triples, Literal(len(self.graph), datatype=XSD.integer)) )
        # void:entities
        n_entities = len([ cl for cl in self.graph.subjects(RDF.type, self.bf.Classification) ])
        n_entities += len([ w for w in self.graph.subjects(RDF.type, self.bf.Work) ])
        n_entities += len([ i for i in self.graph.subjects(RDF.type, self.bf.Instance) ])
        h.remove( (self.abr[''], self.void.entities, None) )
        h.add( (self.abr[''], self.void.entities, Literal(n_entities, datatype=XSD.integer)) )
        # void:rootResource
        h.remove( (self.abr[''], self.void.rootResource, None) )
        for work in self.graph.subjects(RDF.type, self.bf.Work):
            h.add( (self.abr[''], self.void.rootResource, work) )
        h.serialize(void_file, format='turtle')

    def generate_dump_file(self):
        dump_file = 'docs/dump.ttl'
        self.graph.serialize(dump_file, format='turtle')

if __name__ == "__main__":
    bibliography = ABRBibliography()
    print('Generating documentation...')
    bibliography.generate_documentation()
    print('Updating VOID description...')
    bibliography.update_void_description()
    print('Generating dump file...')
    bibliography.generate_dump_file()
    print('Done.')
