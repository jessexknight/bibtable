# BibTable Examples

Here are 5 examples showing how to use the BibTable tool.

Follow these steps to run one example:
 - open a `cmd` window
 - change directory this directory (type `cd DIRNAME`)
 - type the 'Usage' command below

---

### `csv-to-bib/`

Demonstrates copying of tags from `.csv` file into a `.bib` file.

After running the command, check out the `.bib` file before to see the added tags.

Usage:
~~~
.\bibtable.exe .\examples\csv-to-bib\ bib+ -v
~~~

---

### `tex-{basic,advanced}/`

Demonstrates generation of a `.tex` table from tags in a `.bib` file and `.tex` templates.

After running the command, use LaTeX to compile the `main.tex` file in `tex-{basic,advanced}/out/`

Usage - basic:
~~~
.\bibtable.exe .\examples\tex-basic\ tex -o .\examples\tex-basic\out\out.tex -v
~~~

Usage - advanced:
~~~
.\bibtable.exe .\examples\tex-advanced\ bib+ -v
.\bibtable.exe .\examples\tex-advanced\ tex -o .\examples\tex-advanced\out\out.tex -v
~~~

---

### `html-{basic,advanced}/`

Demonstrates generation of a `.html` table from tags in a `.bib` file and `.html` templates.

After running the command, open the `out.html` file in your browser (drag-and-drop or double click)

Usage - basic:
~~~
.\bibtable.exe .\examples\html-basic\ html -o .\examples\html-basic\out\out.tex -v
~~~

Usage - advanced:
~~~
.\bibtable.exe .\examples\html-advanced\ bib+ -v
.\bibtable.exe .\examples\html-advanced\ html -o .\examples\html-advanced\out\out.html -v
~~~

---

#### Notes
- The `-v` option is optional; it outputs the detailed information when BibTable runs. Omit `-v` and this will not print.
- This README file best viewed in a [markdown editor](https://jbt.github.io/markdown-editor/)

