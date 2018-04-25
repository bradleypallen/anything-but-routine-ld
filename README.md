# schottlaender-db

## Overview

This repository contains work towards a linked data representation of
the bibliographical metadata captured in [Anything But Routine](http://escholarship.org/uc/item/0xj4d6bm),
Brian Schottlaender's scholarly bibliography of works by and about William S. Burroughs, the American Beat Generation
author.

## Goals

- Demonstrate the utility of BIBFRAME 2.0 for catalogs of rare materials typical of those generated
by and for rare book collectors and sellers
- Generate lessons learned for the description of such materials in BIBFRAME 2.0 and its proposed extensions
- Provide a platform for in-depth analytics applied to the data in rare book catalogs
- Demonstrate the utility of linked data as a next-generation approach to the creation of online catalogs for rare materials
- Provide a nifty Web presence for my own Burroughs collection

## Approach

- Convert the v4.0 PDF catalog to a set of CSV files, one per instance type (A through I)
- For each instance type CSV file:
    - Manually edit the CSV file to eliminate PDF conversion errors and artifacts
    - Convert the manually cleansed CSV to a set of Turtle files

### Vocabularies

- BIBFRAME 2.0
- ARM

## License

As this work contains adapted material from Schottlaender's
bibliography, in compliance with the terms of its license, we license
this work in the same manner, i.e. under a [Creative Commons
Attribution-NonCommercial-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
(CC BY-NC-SA 4.0) license.
