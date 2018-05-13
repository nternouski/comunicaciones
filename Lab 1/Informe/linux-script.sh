pdflatex -synctex=1 -halt-on-error entregable
bibtex entregable
pdflatex -synctex=1 -halt-on-error entregable
okular entregable.pdf