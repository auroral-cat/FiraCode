#!/bin/bash
set -o errexit -o nounset -o pipefail
cd "$(dirname "$0")/.."
[ -d venv ] && source venv/bin/activate

family_name=${FIRACODE_FAMILY_NAME:-"Fira Code"}
glyphs_file=${FIRACODE_GLYPHS_FILE:-"FiraCode.glyphs"}
italic=${FIRACODE_ITALIC:-0}

dir="distr/otf/${family_name}"

mkdir -p "${dir}"
# the italic is built after the upright and goes next to it
[ "${italic}" -eq 0 ] && rm -rf "${dir:?}/"*

args=( "$@" )
default_weights=( "Light" "Regular" "Retina" "Medium" "SemiBold" "Bold" )
weights=( "${args[@]:-"${default_weights[@]}"}" )

for weight in "${weights[@]}"; do
	style="${weight}"
	[ "${italic}" -ne 0 ] && style="${weight} Italic"
	[ "${style}" = "Regular Italic" ] && style="Italic"
	file="${dir}/FiraCode-${style// /}.otf"

	echo "=============="
	echo
	echo "  [i] Creating ${file}"
	echo

	fontmake -g "${glyphs_file}" -o otf --output-path "${file}" -i "${family_name} ${style}"
done
