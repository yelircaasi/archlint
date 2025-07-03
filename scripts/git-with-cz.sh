#!/bin/env bash

if [[ $1 == "commit" && -z $2 ]]; then
  cz "$@"
elif [[ $1 == "commit" && $2 == "--retry" ]]; then
  cz "$@"
else
  command git "$@"
fi
