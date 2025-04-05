#!/usr/bin/env python3

__version__ = '0.1'
__date__ = '09-05-2024'
__author__ = 'D.J.BERGER'

###### Imports

import os
import sys
import tempfile
import argparse

###### Functions

def switch_names(file1, file2):
	with tempfile.NamedTemporaryFile(delete=False) as tmp:
		temp_name = tmp.name
	try:
		os.rename(file1, temp_name)
		os.rename(file2, file1)
		os.rename(temp_name, file2)
		print(f"Switched names: {file1} <-> {file2}")
	except OSError as e:
		print(f"Error: {e}")
	finally:
		if os.path.exists(temp_name):
			os.remove(temp_name)


def parse_args():
	description = 'Switch the names of two files. Version: %s, Date: %s, Author: %s' % (__version__, __date__, __author__)
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("--file1", required=True, help="First files to be switched")
	parser.add_argument("--file2", required=True, help="Second file to be switched")
	parser.add_argument("--version", action="version", version='Version: %s' % (__version__))

	return parser.parse_args()

###### Main

def main():
	args = parse_args()

	switch_names(args.file1, args.file2)

if __name__ == "__main__":
	main()
