#!/bin/sh

typeset build=true

while [ "$#" -gt "0" ]
do
    case $1 in
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
done

if [ "$build" = "true" ]
then
    hugo
fi

rsync -azx --delete public/ shirabe:/var/www/beta.taricorp.net/public_html/
