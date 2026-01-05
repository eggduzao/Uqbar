#!/bin/bash

# Message
echo "Cleaning system-specific artifacts..."



python -m uqbar milou book -i '/Users/egg/Projects/Uqbar/tests/test_milou/math_query.txt' -o /Users/egg/Projects/Uqbar/tests/test_milou/books/mathematics/ -s 'duckduckgo' -f 'pdf,epub,mobi,azw3,djvu,lit,prc'

python -m uqbar milou book -i '/Users/egg/Projects/Uqbar/tests/test_milou/cs_query.txt' -o /Users/egg/Projects/Uqbar/tests/test_milou/books/computer_science/ -s 'duckduckgo' -f 'pdf,epub,mobi,azw3,djvu,lit,prc'

python -m uqbar milou book -i '/Users/egg/Projects/Uqbar/tests/test_milou/bioinfo_query.txt' -o /Users/egg/Projects/Uqbar/tests/test_milou/books/bioinformatics/ -s 'duckduckgo' -f 'pdf,epub,mobi,azw3,djvu,lit,prc'

python -m uqbar milou book -i '/Users/egg/Projects/Uqbar/tests/test_milou/mldl_query.txt' -o /Users/egg/Projects/Uqbar/tests/test_milou/books/machine_learning/ -s 'duckduckgo' -f 'pdf,epub,mobi,azw3,djvu,lit,prc'

python -m uqbar milou book -i '/Users/egg/Projects/Uqbar/tests/test_milou/med_query.txt' -o /Users/egg/Projects/Uqbar/tests/test_milou/books/medicine/ -s 'duckduckgo' -f 'pdf,epub,mobi,azw3,djvu,lit,prc'

python -m uqbar milou book -i '/Users/egg/Projects/Uqbar/tests/test_milou/biomed_query.txt' -o /Users/egg/Projects/Uqbar/tests/test_milou/books/biomed/ -s 'duckduckgo' -f 'pdf,epub,mobi,azw3,djvu,lit,prc'






# Removendo os arquivos .DS_Store recursivamente.
find . -name ".DS_Store" -type f -delete

# Removendo qualquer outro arquivo de metadados do MAC (arquivos que começam com "._") recursivamente.
find . -name "._*" -type f -delete

# Removendo .Trashes and outros que, às vezes, o MAC gera, quando quer.
find . -name ".Trashes" -type d -exec rm -rf {} +

# Message
echo "Cleaning Python build artifacts..."

# Remove build directories
rm -rf build/ dist/ *.egg-info/ .eggs/

# Remove Python cache and compiled files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*~" -delete

# Remove test and tool caches
rm -rf .pytest_cache/ .mypy_cache/ .tox/ .coverage .cache/

echo "Cleanup complete."

