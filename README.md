# Useful scripts

A repository of scripts/code used across multiple projects.

## *asm_stats.py*
- Calculates common assembly statistics for one or more FASTA files.
- **Input:** takes either a single FASTA or a directory of FASTA files.

Usage:
  ```
  asm_stats.py --fasta <FASTA>

  asm_stats.py --fasta_dir <fasta_dir/>
  ```

Parameters:
```
  -f FILE, --file FILE            Input FASTA file
  --fasta_dir FASTA_DIR           Directory containing FASTA files
  --fasta FASTA                   Single FASTA file
  --gap GAP                       Minimum gap length to be considered a scaffold (optional) [2]
  --output OUTPUT                 Output file prefix (optional) ['sample']
  --version                       Show program's version number and exit
```
* **Output**: CSV file containing assembly metrics with columns:
  * _sampleid_ : Based on the first part of the input fasta (delimeter: '.')
  * _assembly_length_bp_ : Assembly length (bp)
  * _scaffold_count_ : Number of scaffolds
  * _scaffold_N50_bp_ : Scaffold N<sub>50</sub> (bp)
  * _scaffold_N90_bp_ : Scaffold N<sub>90</sub> (bp)
  * _contig_count_ : Number of contigs
  * _contig_N50_bp_ : Contig N<sub>50</sub> (bp)
  * _contig_N90_bp_ : Contig N<sub>90</sub> (bp)
  * _GC_perc_ : GC content (%)
  * _gaps_count_ : Number of gaps (min length to define a gap can be changed with --gap parameter)
  * _gaps_sum_bp_ : Total gap length (bp)
  * _gaps_perc_ : Proportion of genome composed of gaps (%)

## *ari.py*
- Calculates the Adjusted Rand Index between clustering schemes.
- **Input:** takes tab or comma separated files (works on any number of files ≥ 2).
- **Input format:** sample_name,cluster_id 

Usage:
  ```
  ari.py <file1> <file2> <file3>
  ```
- **Output:** pairwise ARI values in both list and matrix format
## *code_similarity.py*
- Calculates the Cosine similarity, Jaccard similarity, longest common substring and Abstract Syntax Tree (optional, not fully tested) between different input files.
- **Input:** two directories of files to be compared (at present must be .md, .R or .py files)

Usage:
  ```
  code_similarity.py --dir1 <first directory/> --dir2 <second directory/>
  ```
Parameters:
```
options:
  -h, --help          show this help message and exit
  --dir1 DIR1         Path to the first directory of scripts
  --dir2 DIR2         Path to the second directory of scripts
  --include-comments  Include comments in the similarity comparison
  --enable-ast        Enable AST-based similarity comparison for Python files
  --keep-duplicates   Keep duplicate lines in the similarity comparison
```
- **Output:** pairwise ARI values in both list and matrix format


## *count_file_differences.py* [ Note: not fully tested ] 
- Counts the pairwise row and column differences between files. 
- **Input:** two directories of CSV files to be compared.

Usage:
  ```
  code_similarity.py --dir1 <first directory/> --dir2 <second directory/> --output <output file prefix>
  ```
Parameters:
```
options:
  -h, --help       show this help message and exit
  --dir1 DIR1      Path to the first directory
  --dir2 DIR2      Path to the second directory
  --output OUTPUT  Output TSV file for comparison results
```
* **Output:** 3 files:
  * _{prefix}.tsv_: Pairwise comparisons between two files, with filenames (cols 1&2), counts of differences by row (col3) or column (col4), names of rows that have changed (col5) and names of columns that have changed (col6)
  * _{prefix}.row_diff_matrix.tsv_: Matrix of pariwise row differences (counts)
  * _{prefix}.col_diff_matrix.tsv_: Matrix of pariwise column differences (counts)

## *fa_select.py*
- Renames, subsets and/or sorts FASTA files. 
- **Input:** FASTA file

Usage:
  ```
  fa_select.py -f <FASTA>
  ```
Parameters:
  ```
  -f FILE, --file FILE            Input FASTA file
  -s, --sort                      Sort by header name
  -l LENGTH, --length LENGTH      Keep only contigs longer than the specified length
  -p PREFIX, --prefix PREFIX      Append prefix to each contig header
  -i INCLUDE, --include INCLUDE   File with list of contig headers to include
  -e EXCLUDE, --exclude EXCLUDE   File with list of contig headers to exclude
  -o OUTPUT, --output OUTPUT      Output file name
  -v, --version                   Show program's version number and exit
  ```
- **Output:** FASTA file

## *split_spreadsheet.py*
- Converts an excel spreadsheet into individual sheets, named after each tab name.

Usage:
  ```
  split_spreadsheet.py -e <spreadsheet> -o  <output directory name>
  ```
Parameters:
  ```
options:
  -h, --help            show this help message and exit
  -e EXCEL_FILE_PATH, --excel_file_path EXCEL_FILE_PATH
                        Path to the Excel file.
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        Directory to save the output files.
  -f {csv,tsv}, --format {csv,tsv}
                        Output format: csv or tsv (default: csv)
  ```
- **Output:** Directory with individual TSV or CSV files

## *switch_names.py*
- Switches the names of two files.
Usage:
  ```
  switch_names.py --file1 <first_file> --file2 <second_file>
  ```
## *unique_values.py*
- For a specified column, returns one representative row containing each unique value in the dataframe. Similiar to 'uniq' on a single column but returns the whole row. 
- **Input:** takes a tab separated file with a header (relevant column must be specified with the --col parameter) and --mode determines whether the first row in a dataframe containing the value is retained or a row is randomly selected.

Usage:
  ```
  unique_values.py --input <input file> --col <column name> --mode <first|random>
  ```


## *annotation_summary_stats.py*
- Calculates summary stats for a transcriptome assembly (CDS or proteins)
- **Input:** takes a FASTA file with nucleotides or protein sequences

Usage:
  ```
  summary_stats.py -f <FASTA>
  summary_stats.py -f <FASTA> --protein
  summary_stats.py -f <FASTA> --trinity
  ```
Parameters:
  ```
Get basic stats for a transcriptome or protein assembly.

options:
  -h, --help         show this help message and exit
  -f, --fasta FASTA  Transcript or protein FASTA file
  --trinity          Parse Trinity-style gene names (for transcript mode)
  --protein          Switch to protein mode (calculates in amino acids)
  ```















