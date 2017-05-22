#!/bin/bash
#
#
#

# OUT_TYPE=csv
OUT_TYPE=html
OUT_FILE_BASE=fraction
OUT_FILE=${OUT_FILE_BASE}.${OUT_TYPE}

rm -i ${OUT_FILE_BASE}.*

./get_topic_tree.py 			\
    --verbose 1				\
    --top-node-slug fraction-arithmetic \
    --out-type ${OUT_TYPE}              \
    --out-file ${OUT_FILE}

# video json example
# https://www.khanacademy.org/api/v1/playlists/arith-review-fractions-intro/videos
