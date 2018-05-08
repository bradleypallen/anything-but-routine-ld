import rdflib, glob, pandas as pd
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS

class ABRBibliography():

    def __init__(self, ttl='edited-ttl/*/*.ttl'):
        self.bf = rdflib.Namespace("http://id.loc.gov/ontologies/bibframe/")
        self.arm = rdflib.Namespace("https://w3id.org/arm/core/ontology/0.1/")
        self.graph = rdflib.Graph()
        self.graph.bind("abri", "https://w3id.org/anything-but-routine/4.0/instance/")
        self.graph.bind("abrw", "https://w3id.org/anything-but-routine/4.0/work/")
        self.graph.bind("bf", "http://id.loc.gov/ontologies/bibframe/")
        self.graph.bind("arm", "https://w3id.org/arm/core/ontology/0.1/")
        for infile in glob.glob(ttl):
            self.graph.parse(infile, format='n3')

    def to_records(self):
        qres = self.graph.query(
            """SELECT DISTINCT ?title ?abrno ?date ?i
               WHERE {
                  ?w rdf:type bf:Work .
                  ?w rdfs:label ?title .
                  ?i bf:instanceOf ?w .
                  ?i bf:identifiedBy ?id .
                  ?id bf:source 'Schottlaender v4.0' .
                  ?id rdf:value ?abrno .
                  ?i bf:provisionActivity ?pa .
                  ?pa bf:date ?date .
               }
               ORDER BY ASC(?date)""")
        results = [ [row[0].toPython(), row[1].toPython(), row[2].toPython(), row[3].toPython() ] for row in qres ]
        instance_df = pd.DataFrame(results, columns=['worktitle', 'id', 'date', 'instance'])
        instance_df['workid'] = instance_df['id'].str[1:-1]
        instance_df['workid'] = instance_df['workid'].apply(pd.to_numeric)
        instance_df['instanceltr'] = instance_df['id'].str[-1]
        instance_df['instanceltr'] = instance_df['instanceltr'].str.upper()
        instance_df['year'] = instance_df['date'].str.extract('\[?(\d\d\d\d)', expand=False)
        instance_df = instance_df.sort_values(by=['workid', 'instanceltr'])
        instance_df = instance_df[['year', 'workid', 'worktitle', 'instanceltr', 'instance']]
        return instance_df.to_dict('records')

    def to_markdown(self, file='docs/index.md'):
        terminating_chars = ['!', '?', '.']
        with open(file, 'w') as mdfile:
            print("# A. BOOKS, BROADSIDES, AND PAMPHLETS", file=mdfile)
            print('', file=mdfile)
            current_work = None
            current_work_title = None
            current_year = '0000'
            for i in self.to_records():
                if i['workid'] != current_work:
                    if i['year'] > current_year:
                        current_year = i['year']
                        print(f"## {current_year}", file=mdfile)
                    current_work = i['workid']
                    current_work_title = i['worktitle']
                    if current_work_title[-1] in terminating_chars:
                        print(f"### A{current_work}. _{current_work_title}_", file=mdfile)
                    else:
                        print(f"### A{current_work}. _{current_work_title}._", file=mdfile)
                instance = URIRef(i['instance'])
                entry = ''

                # bf:identifiedBy
                ids = {}
                for id in self.graph.objects(instance, self.bf.identifiedBy):
                    ids['{}'.format(self.graph.value(id, self.bf.source))] = [ id_str for id_str in self.graph.objects(id, RDF.value) ]

                # Schottlaender no. + bf:title
                schottlaender_id = ids['Schottlaender v4.0'][0]
                # titles can be more complex
                title = self.graph.value(self.graph.value(instance, self.bf.title), RDFS.label)
                if title[-1] in terminating_chars:
                    entry += '#### {}. _{}_ '.format(schottlaender_id[-1].upper(), title)
                else:
                    entry += '#### {}. _{}._ '.format(schottlaender_id[-1].upper(), title)

                # bf:contributor
                for contributor in self.graph.objects(instance, self.bf.contributor):
                    agent = self.graph.value(contributor, RDFS.label)
                    roles = ', '.join([ role for role in self.graph.objects(contributor, self.bf.role) ])
                    entry += '{}, {}; '.format(agent, roles)
                entry = "{}. ".format(entry[:-2])

                # bf:provisionActivity
                for publisher in self.graph.objects(instance, self.bf.provisionActivity):
                    # provisionActivities can have more than one place
                    place = self.graph.value(publisher, self.bf.place)
                    # provisionActivities can have more than one agent
                    agent = self.graph.value(publisher, self.bf.agent)
                    date = self.graph.value(publisher, self.bf.date)
                    entry += '{}: {}, {}; '.format(place, agent, date)
                entry = "{}. ".format(entry[:-2])

                # bf:copyrightDate
                if self.graph.value(instance, self.bf.copyrightDate):
                    entry += '©{}. '.format(self.graph.value(instance, self.bf.copyrightDate))

                # M&M no. (if present)
                if 'Maynard & Miles' in ids:
                    entry += '{M&M ' + ', '.join(ids['Maynard & Miles']) + '}'
                print(entry, file=mdfile)
                print('', file=mdfile)

                # bf.note
                for note in self.graph.objects(instance, self.bf.note):
                    print('- {}'.format(self.graph.value(note, RDF.value)), file=mdfile)
                print('', file=mdfile)

if __name__ == "__main__":
    print('Building bibliography...')
    bibliography = ABRBibliography()
    bibliography.to_markdown()
    print('Done.')
