# schottlaender-db

## Overview

This repository contains work towards a linked data representation of
the bibliographical metadata captured in [Anything But Routine](http://escholarship.org/uc/item/0xj4d6bm),
Brian E.C. Schottlaender's annotated bibliography of works by and about [William S. Burroughs](https://en.wikipedia.org/wiki/William_S._Burroughs), the American Beat Generation
author.

## Goals

- Demonstrate the utility of [BIBFRAME 2.0](http://www.loc.gov/bibframe/docs/index.html) for catalogs of rare materials typical of those created by and for rare book collectors and sellers
- Gain and share experience in the description of such materials in BIBFRAME 2.0 and other BIBFRAME extension ontologies
- Provide a platform for data analytics applied to rare book catalogs, in the spirit of the [Santa Barbara Statement on Collections as Data](https://collectionsasdata.github.io/statement/)
- Demonstrate the utility of linked data combined with Github-style collaboration platforms in creating and maintaining catalogs for rare materials
- Exploit all of the above in building a flashy new resource for [my own Burroughs collection](http://bradleypallen.org/wsb-catalog)

## Approach

- Convert the v4.0 PDF catalog to a set of CSV files, one per instance type (A through I)
- For each instance type CSV file:
    - Manually edit the CSV file to eliminate PDF conversion errors and artifacts
    - Convert the manually cleansed CSV to a set of Turtle files

### Vocabularies

- [BIBFRAME 2.0](http://www.loc.gov/bibframe/docs/index.html)
- [Art and Rare Materials Ontologies](https://github.com/LD4P/arm)

## License

As this work contains adapted material from Schottlaender's
bibliography, in compliance with the terms of its license, we license
this work in the same manner, i.e. under a [Creative Commons
Attribution-NonCommercial-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
(CC BY-NC-SA 4.0) license.
