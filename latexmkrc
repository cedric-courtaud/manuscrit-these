$ENV{'TEXINPUTS'}='./text//:./tex//:' . $ENV{'TEXINPUTS'};

$dvi_previewer = 'start xdvi -watchfile 1.5';
$ps_previewer  = 'start gv --watch';
$pdf_previewer = 'start evince';
$pdflatex = 'pdflatex  %O  --shell-escape %S';