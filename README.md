# BibTable
BibTable is a python tool for adding custom metadata ("tags") to bibliographies.
- Add custom tags to .bib file from .csv
- Dynamical sorting & filtering entries in HTML
- Nice workflow for creating large paper tables in LaTeX

### Adding .csv data to .bib file:
1. Annotate papers with custom tags in a .csv file:
   - Row 1: tag titles
   - Row 2+: papers
   - Col 1: "id" (citation keys)
   - Cols 2+: tags
2. Create a .bib file of the same papers (e.g. from Mendeley)
3. Place .csv and .bib in a folder `INDIR`
4. Run bibtable `bib+` option to add the tags to the .bib file
   - Run `bib-` option to remove the tags from the .bib file

### Generating a table.x {.html or .tex} file from a .bib file
1. Create table templates:
   - table.x: [see examples]
   - entry.x: [see examples]
2. Place both templates and the .bib file in the folder `INDIR`
3. Run {`html`,`tex`} option to create the output file
   - You must specify the output filename as `-o OUTFILE`

### Help [-h] Output
~~~
usage: bibtable.exe [-h] [-o OUTFILE] [-v] INDIR {bib+,bib-,html,tex}
...
positional arguments:
  INDIR                 the directory containing the user-provided files
  {bib+,bib-,html,tex}  do something:
                        bib+: add tags in a csv file to a bib file
                        bib-: remove tags in a csv file from a bib file
                        html: create a html table from a bib file
                        tex:  create a latex table from a bib file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE            the output file name for {html,tex} tables
  -v                    verbose switch
~~~

### Examples
See the examples directory, probably best in this order:
- `csv-to-bib/`
- `tex-basic/`
- `html-basic/`
- `tex-advanced/`
- `html-advanced/`

### Source Code
is available [here](https://github.com/jessexknight/bibtable)


