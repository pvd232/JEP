#!/bin/sh
set -eu
cd "$(dirname "$0")"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$build_dir" concept-note.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$build_dir" concept-note.tex
cp "$build_dir/concept-note.pdf" concept-note.pdf
