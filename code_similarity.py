#!/usr/bin/env python

# Detects similarity between scripts using multiple metrics.

__version__ = '0.1'
__date__ = '09-06-2024'
__author__ = 'D.J.BERGER'

###### Imports

import os
import re
import ast
import argparse
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher


###### Functions

# Cleans code for easier comparison
def preprocess_code(code, include_comments=False, keep_duplicates=False):
	if not include_comments:
		code = re.sub(r'#.*', '', code) # Remove comments
	code = re.sub(r'\s+', ' ', code) # Normalize whitespace
	lines = code.split(';')
	if not keep_duplicates:
		lines = list(set(lines)) # Remove duplicate lines if keep_duplicates is False
	lines = [line.strip() for line in lines if line.strip()]
	if not keep_duplicates:
		lines.sort() # Sort lines to ensure consistent order if duplicates are removed
	return ' '.join(lines)


# Get relevant scripts from target directories
def read_files_from_directory(directory, extensions=(".R", ".md", ".py")):
	files_content = {}
	for filename in os.listdir(directory):
		if filename.endswith(extensions):
			with open(os.path.join(directory, filename), 'r') as file:
				files_content[filename] = file.read()
	return files_content


# Calculate Cosine similarity
def compute_cosine_similarity(text1, text2):
	vectorizer = TfidfVectorizer().fit_transform([text1, text2])
	vectors = vectorizer.toarray()
	return cosine_similarity(vectors)[0, 1]


# Calculate Jaccard similarity
def compute_jaccard_similarity(text1, text2):
	set1 = set(text1.split())
	set2 = set(text2.split())
	intersection = len(set1 & set2)
	union = len(set1 | set2)
	return intersection / union if union != 0 else 0


# Calculate longest common substring
def compute_lcs_similarity(text1, text2):
	seq_matcher = SequenceMatcher(None, text1, text2)
	match = seq_matcher.find_longest_match(0, len(text1), 0, len(text2))
	lcs_length = match.size
	return lcs_length / max(len(text1), len(text2)) if max(len(text1), len(text2)) != 0 else 0


# Calculates AST (optional)
def compute_ast_similarity(ast1, ast2):
	seq_matcher = SequenceMatcher(None, ast1, ast2)
	match = seq_matcher.find_longest_match(0, len(ast1), 0, len(ast2))
	ast_length = match.size
	return ast_length / max(len(ast1), len(ast2)) if max(len(ast1), len(ast2)) != 0 else 0


# Extract AST values from python scripts
def extract_python_ast(file_content):
	try:
		tree = ast.parse(file_content)
		return ast.dump(tree)
	except Exception as e:
		print(f"Error parsing AST for file: {e}")
		return None


# Run main processes
def compare_directories(dir1, dir2, include_comments=False, enable_ast=False, keep_duplicates=False):
	dir1_files = read_files_from_directory(dir1)
	dir2_files = read_files_from_directory(dir2)
	
	similarity_results = []

	for file1_name, file1_content in dir1_files.items():
		for file2_name, file2_content in dir2_files.items():
			preprocessed_file1_content = preprocess_code(file1_content, include_comments, keep_duplicates)
			preprocessed_file2_content = preprocess_code(file2_content, include_comments, keep_duplicates)
			
			cosine_sim = compute_cosine_similarity(preprocessed_file1_content, preprocessed_file2_content)
			jaccard_sim = compute_jaccard_similarity(preprocessed_file1_content, preprocessed_file2_content)
			lcs_sim = compute_lcs_similarity(preprocessed_file1_content, preprocessed_file2_content)
			
			ast_similarity = None
			if enable_ast:
				if file1_name.endswith('.py') and file2_name.endswith('.py'):
					ast1 = extract_python_ast(file1_content)
					ast2 = extract_python_ast(file2_content)
					if ast1 is not None and ast2 is not None:
						ast_similarity = compute_ast_similarity(ast1, ast2)

			similarity_results.append({
				'file1': file1_name,
				'file2': file2_name,
				'cosine_similarity': cosine_sim,
				'jaccard_similarity': jaccard_sim,
				'lcs_similarity': lcs_sim,
				'ast_similarity': ast_similarity
			})

	return similarity_results


# Save results to file
def save_results_to_files(dir1, dir2, similarity_results):
	file1_names = sorted(set(res['file1'] for res in similarity_results))
	file2_names = sorted(set(res['file2'] for res in similarity_results))

	def create_matrix(results, metric):
		matrix = pd.DataFrame(0, index=file1_names, columns=file2_names, dtype=float)
		for res in results:
			matrix.loc[res['file1'], res['file2']] = res[metric] if res[metric] is not None else 0
		return matrix

	cosine_matrix = create_matrix(similarity_results, 'cosine_similarity')
	jaccard_matrix = create_matrix(similarity_results, 'jaccard_similarity')
	lcs_matrix = create_matrix(similarity_results, 'lcs_similarity')
	ast_matrix = create_matrix(similarity_results, 'ast_similarity')

	cosine_matrix.to_csv('cosine_similarity_matrix.csv')
	jaccard_matrix.to_csv('jaccard_similarity_matrix.csv')
	lcs_matrix.to_csv('lcs_similarity_matrix.csv')
	ast_matrix.to_csv('ast_similarity_matrix.csv')

	list_results = []
	for res in similarity_results:
		list_results.append((res['file1'], res['file2'], res['cosine_similarity'], 'Cosine'))
		list_results.append((res['file1'], res['file2'], res['jaccard_similarity'], 'Jaccard'))
		list_results.append((res['file1'], res['file2'], res['lcs_similarity'], 'LCS'))
		if res['ast_similarity'] is not None:
			list_results.append((res['file1'], res['file2'], res['ast_similarity'], 'AST'))

	list_df = pd.DataFrame(list_results, columns=['File1', 'File2', 'Score', 'Metric'])
	list_df.to_csv('similarity_list.csv', index=False)


# Parse arguments from the command line.
def parse_args():
	description = 'Compare scripts from two directories for similarity. Version: %s, Date: %s, Author: %s' % (__version__, __date__, __author__)
	parser = argparse.ArgumentParser(description=description)

	parser.add_argument('--dir1', type=str, help='Path to the first directory of scripts')
	parser.add_argument('--dir2', type=str, help='Path to the second directory of scripts')
	parser.add_argument('--include-comments', action='store_true', help='Include comments in the similarity comparison')
	parser.add_argument('--enable-ast', action='store_true', help='Enable AST-based similarity comparison for Python files')
	parser.add_argument('--keep-duplicates', action='store_true', help='Keep duplicate lines in the similarity comparison')
	parser.add_argument('--version', action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


###### Main
def main():

	args = parse_args()

	similarity_results = compare_directories(args.dir1, args.dir2, args.include_comments, args.enable_ast, args.keep_duplicates)
	save_results_to_files(args.dir1, args.dir2, similarity_results)

if __name__ == "__main__":
	main()
