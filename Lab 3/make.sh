#!/bin/bash

rm ./directory_a/*
rm ./directory_b/*

touch ./directory_a/b.txt ./directory_a/d.gif ./directory_a/e.txt
touch ./directory_b/a.jpg ./directory_b/c.pdf ./directory_b/e.txt

ls ./directory_*
