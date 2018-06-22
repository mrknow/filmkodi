#!/bin/bash

# Update external repos and modules connected with them.

dry=
case "$1" in --dry*) dry=echo;; esac

cd "${0%/*}"

# List of reposytories:
#  kodi-module-name  git-repo-path[@branch/tag/LAST][#subfolder[,subfolder]...] ...
# where "LAST" means last tag
source repos

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
			[[ "$descr" ]] && descr+=$'\n\n'
			descr+="$(awk '/^\s*\[/ {next} /^\s*$/ {if(title) exit} /^./ {title=1; print gensub("^#*\\s*","", 1)}' < "$readme")"
		fi
			return
	done
}

# git pull if a branch
pull()
{
	if git -C "$dir" show-ref --verify refs/heads/"${branch:-master}" >/dev/null 2>&1; then
		local UPSTREAM=${1:-'@{u}'}
		local LOCAL=$(git rev-parse @)
		local REMOTE=$(git rev-parse "$UPSTREAM")
		local BASE=$(git merge-base @ "$UPSTREAM")

		if [[ "$LOCAL" != "$REMOTE" && "$LOCAL" = "$BASE" ]; then
			new_version='y'
		fi
		$dry git -C "$dir" pull
	fi
}

# refresh repo: clone, checkout, pull
# uses: $dir, $repo, $branch
refresh_repo()
{
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
}


date="$(date +'%Y.%m.%d')"
modpath=".."
for line in "${REPOS[@]}"; do
	ver=
	descr=
	summary=
	first_repo=

	read name repos <<< "$line"
	case "$name" in
		"*")    mod="$modpath" ;;
		*.*.*)  mod="$modpath/$name" ;;
		*)      mod="$modpath/script.module.$name" ;;
	esac
	read -a repos <<< $repos

	echo
	echo "----- Updating module $name..."

	echo "${repos[@]}"
	if [[ "${repos[0]}" = "ADDON" ]]; then
		# --- full add-on
		unset 'repos[0]'
		echo ADDON... "${repos[@]}"
		for repo in "${repos[@]}"; do
			IFS='#' read repo irpath _ <<< "$repo"
			IFS='@' read repo branch _ <<< "$repo"
			IFS=',' read -a irpath <<< "$irpath"
			dir="${repo##*/}"
			dir="${dir%.git}"
			if [[ ${#irpath[@]} -eq 0 ]]; then
				irpath=( '.' )
			fi
			# repo contains addon(s)
			refresh_repo
			for d in "${irpath[@]}"; do
				dd="$(readlink -m "$dir/$d")"
				dd="$modpath/${dd##*/}"
				tmpmod="/tmp/kodi-outdated-${mod##*/}"
				[[ -e "$dd" ]] && ($dry rm -rf "$tmpmod"; $dry mv "$dd" "$tmpmod")
				$dry cp -a "$dir/$d" "$mod"
			done
		done
		continue
	fi

	# --- folder for module ---
	$dry mkdir -p "$mod"

	# --- remove old module code ---
	tmpmod="/tmp/kodi-outdated-${mod##*/}-lib"
	[[ -e "$mod/lib" ]] && ($dry rm -rf "$tmpmod"; $dry mv "$mod/lib" "$tmpmod")

	# --- process all git repos in this module ---
	for repo in "${repos[@]}"; do
		IFS='#' read repo irpath _ <<< "$repo"
		IFS='@' read repo branch _ <<< "$repo"
		IFS=',' read -a irpath <<< "$irpath"
		dir="${repo##*/}"
		dir="${dir%.git}"
		new_version=
		[[ "$summary" ]] && summary+=", $dir" || summary="$dir"
		[[ ! "$first_repo" ]] && first_repo="$repo"

		echo
		echo " ---  updating repo $dir..."

		# --- refresh repo ---
		refresh_repo

		# --- auto version ---
		if [[ -z "$ver" ]]; then
			case "$branch" in
				''|master|release)                        ver="$date" ;;
				20[0-9][0-9][.-][01][0-9][.-][0-3][0-9])  ver="${branch//-/.}"; new_version='y' ;;
				20[0-9][0-9][01][0-9][0-3][0-9])          ver="${branch:0:4}.${branch:4:2}.${branch:6:2}"; new_version='y' ;;
				*)                                        ver="$date" ;;
			esac
			ver="$ver.0"
		fi

		# --- read module info ---
		description
		if [[ -n "$dry" ]]; then
			echo " >>> repo='$name'/'${repo##*/}' folders='${irpath[@]}' B='$branch', ver='$ver'"
		fi

		# --- refresh module code ---
		$dry mkdir -p "$mod/lib"
		for d in "${irpath[@]}"; do
			$dry cp -a "$dir/$d" "$mod/lib/"
		done

	done


	[[ ! "$descr" ]] && descr="$name external module"
	if [[ -n "$dry" ]]; then
		echo " >>> repo='$name' ver='$ver', desc='$descr'"
		continue
	fi

	# --- refresh module ---
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
        <summary lang="en">$summary module</summary>
        <description lan="en">$descr</description>
        <license>LICENSE</license>
        <platform>all</platform>
        <email></email>
        <website>${first_repo%.git}</website>
        <forum></forum>
        <source>${first_repo%.git}</source>
        <language></language>
   </extension>
</addon>
EOF
		echo
		echo "  ###  Please, update '$(readlink -f "$mod/addon.xml")'"
		echo "       Especially AUTHOR and LICENSE."
		echo "       See ${first_repo%.git}"
		echo
	fi

	if [[ ! -e "$mod/LICENSE.txt" ]]; then
		cat > "$mod/LICENSE.txt" << EOF
Here should be module $name license.
Please update this file.
See ${repo%.git}
EOF
		echo "  ###  Please, update '$(readlink -f "$mod/LICENSE.txt")'"
		echo "       See ${first_repo%.git}"
		echo
	fi

	[[ ! -e "$mod/icon.png" ]] && cp icon.png "$mod/icon.png"

done

