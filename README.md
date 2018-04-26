# anything-but-routine-ld

## Overview

This repository contains work towards a linked data representation of
the bibliographical metadata captured in [Anything But Routine (ABR)](http://escholarship.org/uc/item/0xj4d6bm),
Brian E.C. Schottlaender's annotated bibliography of works by and about [William S. Burroughs](https://en.wikipedia.org/wiki/William_S._Burroughs), the American Beat Generation
author.

## Goals

- Demonstrate the utility of [BIBFRAME 2.0](http://www.loc.gov/bibframe/docs/index.html) for catalogs of rare materials typical of those created by and for rare book collectors and sellers
- Gain and share experience in the description of such materials in BIBFRAME 2.0 and other BIBFRAME extension ontologies
- Provide a platform for data analytics applied to rare book catalogs, in the spirit of the [Santa Barbara Statement on Collections as Data](https://collectionsasdata.github.io/statement/)
- Demonstrate the utility of linked data combined with Github-style collaboration platforms in creating and maintaining catalogs for rare materials
- Exploit all of the above in building a flashy new linked data resource for [my own Burroughs collection](http://bradleypallen.org/wsb-catalog)

## Disclaimer

Early days here. Still working out the details and best practices to apply. A long way yet to go to get beyond ABR's A list. I'm not a trained cataloger, though if you hum a few bars I can fake it. Just kidding.

## Approach

I'm focusing on using [BIBFRAME 2.0](http://www.loc.gov/bibframe/docs/index.html) primarily, with a few classes and modeling recommendations taken from the rapidly evolving [Art and Rare Materials Ontologies](https://github.com/LD4P/arm).

I currently start out with two notebooks, each implementing a part of the workflow involved.

- [generate-csv-from-pdf](https://github.com/bradleypallen/schottlaender-db/blob/master/generate-csv-from-pdf.ipynb): Convert the ABR v4.0 .pdf catalog to a set of .csv files, one per instance type A through I
- For each instance type .csv file:
    - *Manually edit* the .csv file to eliminate PDF conversion errors and artifacts
    - [generate-ttl-from-csv](https://github.com/bradleypallen/schottlaender-db/blob/master/generate-ttl-from-csv.ipynb): Convert the manually cleansed .ttl to a set of Turtle files
- For each generated .ttl file:
    - *Manually edit* the .ttl files to apply modeling best practices that aren't automated in the above step

The PDF-to-text conversion can't handle a lot of the notes in the instance annotations, which I am modeling using bf:Note. That's the reason for the manual step in the above workflow. I'm not sure that I will be able to improve that to any degree, but I may be able to reduce the tweaking to a minimum. In any case, working with the .pdf and .csv files is only a transitional phase to get the bibliographic data into .ttl files under Git version control.

Once the workflow has been completely executed, it should be possible to work moving forward off of the .ttl files, without further reference to the source .pdf and .csv files.

[generate-graph-from-ttl](https://github.com/bradleypallen/schottlaender-db/blob/master/generate-graph-from-ttl.ipynb) hints at what's possible once we've gotten things to that stage. It loads all of the .ttl files into an rdflib.Graph and shows how the graph can be queried and query results visualized. It hints at the ability to generate future versions of ABR directly from the graph, and at the use of collaborative Git-based development of the data in the individual .ttl files to be where the work of catalog refinement and maintenance is done in the future.

## License

As this work contains adapted material from Schottlaender's
bibliography, in compliance with the terms of its license, we license
this work in the same manner, i.e. under a [Creative Commons
Attribution-NonCommercial-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
(CC BY-NC-SA 4.0) license.
