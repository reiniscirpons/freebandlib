#!/bin/sh
BASE_URL="https://github.com/reiniscirpons/freebandlib/releases/download"
TAG="v0.0.1"
OUT_DIR="./benchmarks/samples"
mkdir -p $OUT_DIR

PREFIX="interval_transducers_"
curl -L "$BASE_URL/$TAG/$PREFIX[00-19].gz" -o "$OUT_DIR/$PREFIX#1.gz"
PREFIX="minimal_transducers.gz"
curl -L "$BASE_URL/$TAG/$PREFIX" -o "$OUT_DIR/$PREFIX"
PREFIX="word-samples.tar.gz"
curl -L "$BASE_URL/$TAG/$PREFIX" -o "$OUT_DIR/$PREFIX"
tar -xf $OUT_DIR/$PREFIX
rm $OUT_DIR/$PREFIX
