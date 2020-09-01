MICROBENCHMARKS_TEMPLATE := scripts/microbenchmark_template.py

all: figures/microbenchmark_tmp_rcw_1_1_2.pdf figures/microbenchmark_tmp_rcw_3_3_6.pdf figures/microbenchmark_tmp_rcw_6_6_12.pdf figures/microbenchmark_tmp_rcwc_1_1_2.pdf figures/microbenchmark_tmp_rcwc_3_3_6.pdf figures/microbenchmark_tmp_rcwc_6_6_12.pdf

figures/microbenchmark_tmp_rcw_1_1_2.pdf: ${MICROBENCHMARKS_TEMPLATE}
	python $^ rcw 1 1 2 25 $@

figures/microbenchmark_tmp_rcw_3_3_6.pdf: ${MICROBENCHMARKS_TEMPLATE}
	python $^ rcw 3 3 6 25 $@

figures/microbenchmark_tmp_rcw_6_6_12.pdf: ${MICROBENCHMARKS_TEMPLATE}
	python $^ rcw 6 6 12 25 $@

figures/microbenchmark_tmp_rcwc_1_1_2.pdf: ${MICROBENCHMARKS_TEMPLATE}
	python $^ rcwc 1 1 1 25 $@

figures/microbenchmark_tmp_rcwc_3_3_6.pdf: ${MICROBENCHMARKS_TEMPLATE}
	python $^ rcwc 3 3 3 25 $@

figures/microbenchmark_tmp_rcwc_6_6_12.pdf: ${MICROBENCHMARKS_TEMPLATE}
	python $^ rcwc 6 6 6 25 $@
