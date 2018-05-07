# anything-but-routine-ld

## Overview

This repository contains work towards a linked data representation of
the bibliographical metadata captured in [Anything But Routine (ABR)](http://escholarship.org/uc/item/0xj4d6bm),
Brian E.C. Schottlaender's annotated bibliography of works by and about [William S. Burroughs](https://en.wikipedia.org/wiki/William_S._Burroughs), the American Beat Generation
author.

### License

As this work contains adapted material from Schottlaender's
bibliography, in compliance with the terms of its license, we license
this work in the same manner, i.e. under a [Creative Commons
Attribution-NonCommercial-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
(CC BY-NC-SA 4.0) license.

### Disclaimer

Early days here. Still working out the details and best practices to apply. A long way yet to go to get beyond ABR's A list. I'm not a trained cataloger, though if you hum a few bars I can fake it. Just kidding.

## Goals

- Demonstrate the utility of [BIBFRAME 2.0](http://www.loc.gov/bibframe/docs/index.html) for bibliographies and catalogs of rare materials typical of those created by and for rare book collectors and sellers
- Gain and share experience in the description of such materials in BIBFRAME 2.0 and other BIBFRAME extension ontologies
- Provide a platform for data analytics applied to rare book bibliographies and catalogs, in the spirit of the [Santa Barbara Statement on Collections as Data](https://collectionsasdata.github.io/statement/)
- Demonstrate the utility of linked data combined with Github-style collaboration platforms in creating and maintaining bibliographies and catalogs for rare materials
- Exploit all of the above in building a flashy new linked data resource for [my own Burroughs collection](http://bradleypallen.org/wsb-catalog)

## Approach

### Modeling

I'm using [BIBFRAME 2.0](http://www.loc.gov/bibframe/docs/index.html) primarily, with a few classes and modeling recommendations taken from the rapidly evolving [Art and Rare Materials Ontologies](https://github.com/LD4P/arm).

The experience so far has been natural, with the work/instance distinction implicit in ABR easily made explicit in the model. Most of the information in instances can be easily captured using a handful of attributes, specifically:

- bf:contributor
- bf:copyrightDate
- bf:identifiedBy
- bf:instanceOf
- bf:note
- bf:provisionActivity
- bf:title

To start with, I'm using string literals to express the basic information in the associated instantiations of bf:Agent, bf:Identifier, bf:Note, and bf:provisionActivity. In the long run, my plan is to work on using various entity resolution resources to augment the labels with URI references linking out to other resources such as Wikidata, DBPedia and/or Library of Congress linked data. For relators in the bf:role of a bf:Agent, I've been trying to keep to the term recommendations in the [LC MARC Code List for Relators.](http://www.loc.gov/marc/relators/relaterm.html)

There are a number of unresolved modeling issues that I plan to chip away at. These include:

- _Preserving the ordering of notes_: one of the long-standing and less-charming aspects of RDF is its lack of respect for preserving order in data elements. This causes trouble when generating a version of ABR directly from the RDF graph. There are hacks to address this but they will add complexity to what is currently a pretty straightforward representation. [Dan Brickley has recently begun to grapple with this issue](https://github.com/schemaorg/schemaorg/issues/1910) in the context of schema.org and the evolution of JSON-LD, so maybe in the future we can solve this by moving from Turtle to JSON-LD as our choice of serialization.
- _Representing uncertainty about publication agents, dates and places_: ABR makes liberal use of cataloger's conventions for encoding uncertainty into strings using square brackets and question marks. I'd like to address this by using arm:InaccuracyNote in conjunction with bf:provisionActivity.
- _Representing citations within notes_: ABR frequently adds citations to specific notes that make reference to other bibliographies or catalogs. I'd like to understand how to augment a bf:Note with that information.
- _Converting document forward references into links_: Notes also make reference to other items in the bibliography, for example when expressing the relationship between a book and earlier appearances of material in article form.
- _Allocating descriptive information between works and instances_: My first cut at the work/instance partitioning of ABR skews heavily towards instances, with little data expressed at the bf:Work level other than the title and links to the various instances of the work. This does not reflect Schottlaender's practice where he often combines a work and instance together into a single record with a single identifier (e.g., A9). In this first pass, I've expediently ignored this nuance, and as a result, have coined identifiers that don't exist in ABR (e.g., A9a). That in itself is a bug that I'll have to address at some point. In addition, however, there are choices to be made across all of the works on which pieces of descriptive information are hung on those works, and implicitly inherited down to their instances, and which have their scope restricted to specific instances. I'm optimistic that these choices can be automated by being cleverer about exploiting the structure in the ABR text.
- _Representing binding information_: There is a lot of information about how instances in ABR are bound; in the [generate-ttl-from-csv notebook](https://github.com/bradleypallen/anything-but-routine-ld/blob/master/generate-ttl-from-csv.ipynb) , you can see that there are 23 different phrases in the notes that contain the string "bound". I expect to exploit the arm:Binding class to capture that information.

Besides these issues, there's undoubtedly a bunch more. Once things are in .ttl files, it will be easy to load them into RDF graphs and then into pandas DataFrames to do the exploratory analysis to determine how best to squeeze more structured data out of the notes and the related items.

### Workflow

The workflow, as it is currently implemented, is shown below:

![[Converting Anything But Routine v4.0 into linked data]](workflow.png)

In the next few sections we describe the various steps in this workflow. (NOTE: the current implementation has only addressed the ABR A list. Work remains to generalize that into code that processes the entire set of data extracted from ABR, but in the following we'll talk as if that's already done.)

#### 1. Generating .csv files from the ABR .pdf

I'm using the [PyPDF2 python library](http://mstamy2.github.io/PyPDF2/) to convert the .pdf file into text. It works, but not very well, on the ABR .pdf file; in the notes, a lot of quotations and other challenging characters get dropped. But it's sufficient to allow me to pattern match against the identifiers and split the text into chunks, each containing the relevant text for that specific instance. I load that into a pandas DataFrame, and do some simple regexp-based extraction of publications, titles and dates from the instance text, saving all of the converted text for an instance to a notes column, then save the DataFrame to .csv files, one per ABR work category. _([generate-csv-from-pdf.ipynb](https://github.com/bradleypallen/anything-but-routine-ld/blob/master/generate-csv-from-pdf.ipynb))_


#### 2. Manual cleansing of the .csv files

Because the notes are poorly handled in the .pdf conversion process, I load the .csv file for each category into a spreadsheet application, and then, row by instance row, make corrections to the text in the notes column, with a fair amount of cutting-and-pasting from the original document. Thank God that works.

#### 3. Generating .ttl files from the .csv files

From the cleansed .csv files, I load them into a pandas DataFrame, do some additional information extraction (using both simple regexps and tooling from the [NLTK natural language processing library](http://www.nltk.org/index.html)), and then iterate through the instances to generate triples which are added to an RDF graph build using the [rdflib Python library](http://rdflib.readthedocs.io/en/stable/). Each instance is serialized out to a .ttl file (which choice of serialization seems to be standard within BIBFRAME and ARM circles). We then generate a .ttl file for each work, adding the links to their coorresponding instances.
_([generate-ttl-from-csv.ipynb](https://github.com/bradleypallen/anything-but-routine-ld/blob/master/generate-ttl-from-csv.ipynb))_

#### 4. Manual cleansing of the .ttl files

The out-of-the-box NLTK sentence tokenization, while useful, doesn't do a great job when confronted with abbreviations and such. In a similar vein, using NLTK's entity chunking to generate values for bf:contributor generates a certain amount of noise in addition to the convenience factor. So I examine and correct each generated .ttl file as needed, comparing it to the entry in the original document, mostly editing notes and agents.

#### 5. Generating an RDF graph from the .ttl files

The data now captured in .ttl files, one per bf:work and bf:Instance, is parsed into an rdflib.Graph. From there, we can explore and visualize the data using either SPARQL queries or by directly walking the graph using rdflib's RDF graph iterators. For ease of analysis, I'm finding that first hewing out data using one or both of those approaches and then creating a pandas DataFrame is a great way to go. The (partial) bibliography at [doc/index.md](doc/index.md) is generated using that approach. Bringing the ABR data into a Python notebook environment, together with the use of collaborative Git-based maintenance of the data points towards a way in which the work of catalog refinement and maintenance can be done in the future. _([generate-graph-from-ttl.ipynb](https://github.com/bradleypallen/anything-but-routine-ld/blob/master/generate-graph-from-ttl.ipynb))_

## Roadmap

Beyond cleaning up the horribly ugly chunks of code in the notebooks and chipping away at the modeling issues mentioned above, once the representation of ABR as linked data is mature I want to address the logistics of publishing it on the open linked data Web in a way that will be both sustainable and useful. As hinted at above, I think hewing closely to a minimalist approach based on notebooks and git will be key.

## Acknowledgements

Only one, really, at this point: thanks to Brian Schottlaender for the huge amount of effort and devotion that went into the creation of Anything But Routine.
