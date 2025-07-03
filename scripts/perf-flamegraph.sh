#!/bin/env bash

if ! command -v perf &>/dev/null; then
  echo "'perf' is not installed."
else
  perf record -o codeqa/performance/perf/perf.data hello
  flamegraph \
    -o codeqa/performance/perf/flamegraph.svg \
    --perfdata codeqa/performance/perf/perf.data
fi
