#!/usr/bin/env bash

# Root directory (base)
ROOTDIR="/Users/egg/Projects/Uqbar/src/"

OUTER_LIST=(
  "apollo"
  "blacksmith"
  "bloom"
  "fabric"
  "musique"
  "olympus"
  "wildlife"
)

for EL1 in "${OUTER_LIST[@]}"; do

    SUBDIR="${ROOTDIR}${EL1}/subpackage/"
    CLIDIR="${ROOTDIR}${EL1}/cli/"
    COMDIR="${ROOTDIR}${EL1}/cli/commands/"

    mkdir -p $SUBDIR
    mkdir -p $CLIDIR
    mkdir -p $COMDIR
    touch "${CLIDIR}__init__.py"
    touch "${CLIDIR}main.py"
    touch "${COMDIR}__init__.py"

    if [ $EL1 == "apollo" ]; then
      INNER_LIST=(
        "syzygy"
        "perseid"
        "parallax"
      )
    fi
    if [ $EL1 == "blacksmith" ]; then
      INNER_LIST=(
        "quench"
        "rivet"
      )
    fi
    if [ $EL1 == "bloom" ]; then
      INNER_LIST=(
        "timberline"
        "cradle"
      )
    fi
    if [ $EL1 == "fabric" ]; then
      INNER_LIST=(
        "phenoteka"
        "staircase"
      )
    fi
    if [ $EL1 == "musique" ]; then
      INNER_LIST=(
        "unison"
        "flute"
        "sonata"
        "violin"
        "duet"
        "xylophone"
        "ukulele"
      )
    fi
    if [ $EL1 == "olympus" ]; then
      INNER_LIST=(
        "keres"
        "elf"
        "janus"
        "yara"
        "glyphic"
        "vulkanic"
        "namtar"
        "inkanyamba"
        "qetesh"
        "hint"
        "faun"
        "dryad"
        "triskelion"
        "zephyr"
      )
    fi
    if [ $EL1 == "wildlife" ]; then
      INNER_LIST=(
        "nightingale" # (TryDINN)
        "leopard" # (LumenNet)
      )
    fi

    # ===== LOOP INTERNO =====
    for EL2 in "${INNER_LIST[@]}"; do

        SUBTOOLDIR="${SUBDIR}${EL2}/"

        mkdir -p $SUBTOOLDIR
        touch "${COMDIR}${EL2}_cmd.py"


    done

    echo
done

mkdir -p _apollo
mkdir -p _blacksmith
mkdir -p _bloom
mkdir -p _fabric
mkdir -p _musique
mkdir -p _olympus
mkdir -p _uqbar
mkdir -p _wildlife

# 1. Basic Syntax
# The statement must start with if, include then, and end with fi (if backwards). 
# bash
# if [ condition ]; then
#     # Commands to run if true
# fi

# 2. Common Comparison Types
# Bash uses specific brackets for different types of tests: 
# Type  Syntax  Use Case
# Simple Test [ $x -eq 1 ]  Basic portability (POSIX sh compatible).
# Advanced  [[ $x == "a" ]] Recommended for Bash. Supports pattern matching and regex.
# Arithmetic  (( $x > 5 ))  For mathematical operations and integer comparisons.
# 3. Comparison Operators
# Numbers 
# -eq : Equal to
# -ne : Not equal to
# -gt : Greater than
# -lt : Less than
# -ge : Greater than or equal to
# Strings 
# == or = : Equal to
# != : Not equal to
# -z : String is empty
# -n : String is not empty 
# Files 
# -e : File exists
# -f : Is a regular file (not a directory)
# -d : Is a directory
# -x : File is executable 

# 4. Full Example (if-elif-else)
# You can chain multiple conditions using elif and provide a fallback with else. 
# bash
# #!/bin/bash
# count=10

# if [ $count -gt 15 ]; then
#     echo "Count is greater than 15"
# elif [ $count -eq 10 ]; then
#     echo "Count is exactly 10"
# else
#     echo "Count is something else"
# fi

# 5. Combining Conditions
# Use logical operators to test multiple expressions at once. 
# AND: [[ $a -gt 1 && $b -lt 10 ]]
# OR: [[ $a -eq 1 || $b -eq 2 ]]
# Critical Formatting Rules
# Spaces are mandatory: There must be a space after [ and before ] (e.g., [ $x == 1 ] not [$x==1]).
# Quotes: Always wrap variables in double quotes (e.g., "$var") to prevent errors if the variable contains spaces or is empty.
