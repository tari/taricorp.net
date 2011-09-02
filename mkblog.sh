#!/bin/bash

read -p "Entry title: " TITLE
SLUG=$(echo $TITLE | tr " " "-")
read -p "Slug [$SLUG]: " SLUG

NOW=`date +%Y-%m-%d`
sed s/CREATION_DATE/`date +%Y-%m-%d`/g blog-template.html > site/content/blog/`date +%Y`/$SLUG.html

