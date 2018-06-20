#!/bin/bash

SSH_REPO="kodi.sharkbits.com:/home/kodi/www"

cd "${0%/*}"

do_build=
do_upload=

usage()
{
	echo "${0##*/} [-b] [-u] [repo]"
	exit 1
}

help()
{
	echo "${0##*/} [-b] [-u] [repo]"
	echo
	echo "Where -b for build, -u for upload, repo name"
	echo "Default -b -u filmkodi"
	exit 0
}

[[ "$1" = "--help" ]] && help
while getopts ":bu" opt; do
	case "${opt}" in
		b) do_build=y ;;
		u) do_upload=y ;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND-1))


# default
repo="${1:-filmkodi}"
out="./out/$repo"

if [[ ! "$do_build" && ! "$do_upload" ]]; then
	do_build=y
	do_upload=y
fi

mkdir -p "$out"

if [[ "$do_build" = y ]]; then
	./addon_generator.py "$repo"

	while read addon ver; do
		if [[ -s "$out/$addon/$addon-$ver.zip" ]]; then
			echo "---  [ $addon // $ver ]  ... already exists. Skipping."
		else
			echo "---  [ $addon // $ver ]"
			mkdir -p "$out/$addon"
			zip -r "$out/$addon/$addon-$ver.zip" "$addon" -x '*.pyc' '*.pyo' '*/core' '*/.*.sw?' '*/.git'
		fi
	done <<< $(awk '/<addon id=/ { print(gensub("^.* id=\"([^\"]*)\".* version=\"([^\"]*)\".*$", "\\1 \\2", 1))}' "$out/addons.xml")
fi


if [[ "$do_upload" = y ]]; then
	#scp -P 5551 -r $out/* $SSH_REPO/$repo/
	rsync -aPe 'ssh -p 5551' $out/ $SSH_REPO/$repo/
fi
