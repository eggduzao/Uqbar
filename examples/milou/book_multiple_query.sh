#!/bin/bash

cd '/Users/egg/Projects/Uqbar/src/'

# Searching Bioinformatics Books
echo "Searching Bioinformatics Books..."
python -m uqbar milou book \
	   -i '/Users/egg/Projects/Uqbar/tests/test_milou/bioinfo_query.txt' \
	   -o '/Users/egg/Projects/Uqbar/tests/test_milou/books/bioinformatics/' \
	   -s 'duckduckgo' \
	   -f 'pdf' \

# Searching Machine Learning Books
echo "Searching Machine Learning Books..."
python -m uqbar milou book \
	   -i '/Users/egg/Projects/Uqbar/tests/test_milou/mldl_query.txt' \
	   -o '/Users/egg/Projects/Uqbar/tests/test_milou/books/machine_learning/' \
	   -s 'duckduckgo' \
	   -f 'pdf' \

# Searching Medicine Books
echo "Searching Medicine Books..."
python -m uqbar milou book \
	   -i '/Users/egg/Projects/Uqbar/tests/test_milou/med_query.txt' \
	   -o '/Users/egg/Projects/Uqbar/tests/test_milou/books/medicine/' \
	   -s 'duckduckgo' \
	   -f 'pdf' \

# Searching Biomedicine Books
echo "Searching Biomedicine Books..."
python -m uqbar milou book \
	   -i '/Users/egg/Projects/Uqbar/tests/test_milou/biomed_query.txt' \
	   -o '/Users/egg/Projects/Uqbar/tests/test_milou/books/biomed/' \
	   -s 'duckduckgo' \
	   -f 'pdf' \

# Searching Computer Science Books
echo "Searching Computer Science Books..."
python -m uqbar milou book \
	   -i '/Users/egg/Projects/Uqbar/tests/test_milou/cs_query.txt' \
	   -o '/Users/egg/Projects/Uqbar/tests/test_milou/books/computer_science/' \
	   -s 'duckduckgo' \
	   -f 'pdf' \

# Searching Mathematics Books
echo "Searching Mathematics Books..."
python -m uqbar milou book \
	   -i '/Users/egg/Projects/Uqbar/tests/test_milou/math_query.txt' \
	   -o '/Users/egg/Projects/Uqbar/tests/test_milou/books/mathematics/' \
	   -s 'duckduckgo' \
	   -f 'pdf' \

echo "Download complete."

