#!/bin/sh

hugo && rsync -azx --delete public/ shirabe:/var/www/beta.taricorp.net/public_html/
