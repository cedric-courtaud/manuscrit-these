OUTPUT_DIR := build
LATEXMK := latexmk -bibtex -output-directory=${OUTPUT_DIR} -pdf 

paper: main.tex
	${LATEXMK} $< 

preview: main.tex
	${LATEXMK} -pv   $< 

live-preview: main.tex
	${LATEXMK} -pvc   $< 

clean: 
	latexmk -output-directory=${OUTPUT_DIR} -c

clean-all: 
	latexmk -output-directory=${OUTPUT_DIR} -C


.PHONY: paper 
