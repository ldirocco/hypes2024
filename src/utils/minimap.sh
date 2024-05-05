cat data/*.fastq  > data/reads.fq
minimap2 -x ava-pb --dual=yes  reads.fq reads.fq |awk '$11>=500' |fpa drop --same-name --internalmatch - > data/overlap.paf 
