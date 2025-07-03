if [ -z $1 ]; then _justfile="justfile"; else _justfile=$1; fi
echo "Formatting $PWD/$_justfile"
just --fmt --unstable
