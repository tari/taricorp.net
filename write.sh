#!/bin/sh

hugo server -D --bind 0.0.0.0 -b http://$(hostname)
