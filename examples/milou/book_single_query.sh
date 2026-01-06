#!/bin/bash

cd '/Users/egg/Projects/Uqbar/src/'

python -m uqbar milou book \
	   -q 'foundations modern probability kallenberg' \
	   -o /Users/egg/Projects/Uqbar/tests/test_milou/books/single/ \
	   -s 'duckduckgo' \
	   -f 'pdf,epub'

