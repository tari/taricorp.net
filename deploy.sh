#!/bin/sh

typeset build=true
typeset hugoopts=""

while [ "$#" -gt "0" ]
do
    case $1 in
        -D)
            hugoopts="$hugoopts -D"
            ;;
        --no-build)
            build=false
            ;;
        --debug)
            set -x
            ;;
        *)
            echo "Unrecognized option: $1" >&2
            exit 1
            ;;
    esac
    shift
done

if [ "$build" = "true" ]
then
    hugo $hugoopts
fi

rsync -avzx --delete public/ shirabe:/var/www/beta.taricorp.net/public_html/
