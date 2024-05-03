# cat data/*.fastq  data/*.ref > data/reads.fq
cat data/*.fastq  > data/reads.fq
minimap2 -x ava-pb  data/reads.fq data/reads.fq > data/ovlp.paf 