#!/bin/bash

# Update external repos and modules connected with them.

# List of reposytories:
#  kodi-module-name  git-repo-path[#subfolder[,subfolder]...]  [branch/tag/LAST]
# where "LAST" means last tag
REPOS=(
	'js2py      https://github.com/PiotrDabkowski/Js2Py.git#js2py               '
	'pyjsparser https://github.com/PiotrDabkowski/pyjsparser.git#pyjsparser     '
	'youtubedl  https://github.com/rg3/youtube-dl.git#youtube_dl            LAST'
)

dry=

cd "${0%/*}"

# checkout to branch $branch (or LAST)
checkout()
{
	[[ "$branch" = "LAST" ]] && branch="$(git -C "$dir" tag --sort version:refname | tail -1)"
	[[ -n "$branch" ]] && $dry git -C "$dir" checkout "$branch"
}

# guess module description
description()
{
	local readme
	for readme in "$dir/README.md" "$dir/README"; do
		if [[ -r "$readme" ]]; then
			descr="$(awk '/^\s*\[/ {next} /^\s*$/ {if(title) exit} /^./ {title=1; print gensub("^#*\\s*","", 1)}' < "$readme")"
		fi
			return
	done
	descr="$name external module"
}

# git pull if a branch
pull()
{
	if git -C "$dir" show-ref --verify refs/heads/"${branch:-master}" >/dev/null 2>&1; then
		local UPSTREAM=${1:-'@{u}'}
		local LOCAL=$(git rev-parse @)
		local REMOTE=$(git rev-parse "$UPSTREAM")
		local BASE=$(git merge-base @ "$UPSTREAM")

		if [ $LOCAL != $REMOTE -a $LOCAL = $BASE ]; then
			new_version='y'
		fi
		$dry git -C "$dir" pull
	fi
}


for line in "${REPOS[@]}"; do
	read name repo branch _ <<< "$line"
	IFS='#' read repo irpath _ <<< "$repo"
	IFS=',' read -a irpath <<< "$irpath"
	dir="${repo##*/}"
	dir="${dir%.git}"
	mod="../script.module.$name"
	new_version=

	echo
	echo "----- Updating module $name..."

	# --- refresh repo ---
	if [[ -d "$dir/.git" ]]; then
		# already cloned, update
		if [[ -n "$branch" ]]; then
			$dry git -C "$dir" fetch
			checkout
		fi
		# git pull if a branch
		pull
	elif [[ -d "$dir" ]]; then
		# Not a git!
		echo "Directory '$dir' exists but it is NOT a git repo! Fix it!"
		exit 1
	else
		# Clone new gir repo
		$dry git clone "$repo"
		if [[ -n "$branch" ]]; then
			checkout
		fi
	fi

	# --- auto version ---
	date="$(date +'%Y.%m.%d')"
	case "$branch" in
		''|master|release)                        ver="$date" ;;
		20[0-9][0-9][.-][01][0-9][.-][0-3][0-9])  ver="${branch//-/.}"; new_version='y' ;;
		20[0-9][0-9][01][0-9][0-3][0-9])          ver="${branch:0:4}.${branch:4:2}.${branch:6:2}"; new_version='y' ;;
		*)                                        ver="$date" ;;
	esac
	ver="$ver.0"

	# --- refresh module info ---
	description
	if [[ -n "$dry" ]]; then
		echo " >>> repo='$name' folders='${irpath[@]}' B='$branch', ver='$ver', desc='$descr'"
		continue
	fi

	mkdir -p "$mod"
	if [[ -e "$mod/addon.xml" ]]; then
		[[ 'y' = "$new_version" ]] && sed -i '/<addon / { s/version="[^"]*"/version="'"$ver"'"/ }' "$mod/addon.xml"
	else
		echo "*" > "$mod/.gitignore"

		cat > "$mod/addon.xml" << EOF
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<addon id="script.module.$name" name="$name" provider-name="AUTHOR" version="$ver">
  <requires>
    <import addon="xbmc.python" version="2.14.0" />
  </requires>
  <extension library="lib" point="xbmc.python.module" />
  <extension point="xbmc.addon.metadata">
        <summary lang="en">$name module</summary>
        <description lan="en">$descr</description>
        <license>LICENSE</license>
        <platform>all</platform>
        <email></email>
        <website>${repo%.git}</website>
        <forum></forum>
        <source>${repo%.git}</source>
        <language></language>
   </extension>
</addon>
EOF
		echo
		echo "  ###  Please, update '$(readlink -f "$mod/addon.xml")'"
		echo "       Especially AUTHOR and LICENSE."
		echo "       See ${repo%.git}"
		echo
	fi

	if [[ ! -e "$mod/LICENSE.txt" ]]; then
		cat > "$mod/LICENSE.txt" << EOF
Here should be module $name license.
Please update this file.
See ${repo%.git}
EOF
		echo "  ###  Please, update '$(readlink -f "$mod/LICENSE.txt")'"
		echo "       See ${repo%.git}"
		echo
	fi

	[[ ! -e "$mod/icon.png" ]] && cp icon.png "$mod/icon.png"

	# --- refresh module code ---
	tmpmod="/tmp/kodi-outdated-${mod##*/}-lib"
	[[ -e "$mod/lib" ]] && ($dry rm -rf "$tmpmod"; $dry mv "$mod/lib" "$tmpmod")
	mkdir -p "$mod/lib"
	for d in "${irpath[@]}"; do
		$dry cp -a "$dir/$d" "$mod/lib/"
	done
done

