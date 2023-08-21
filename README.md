[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository contains code for automated paper scraping, information extraction from papers using chatGPT and IE with this information/papers using vector database and chatGPT
 #### Getting papers from arxiv scraper
 ```bash
 python3 get_papers.py --download_directory --num_papers
 ```
 where the arguments:
 - `download_directory` refers to the path where the papers will be stored
 - `num_papers` number of papers on the topic

 #### Information extraction using chat GPT
 ```bash
 python3 get_papers.py --download_pdfs_directory --extracted_info_csv --open_api_key --readable_csv
 ```
 where the arguments:
 - `download_pdfs_directory` refers to the path where the papers are stored
 - `extracted_info_csv` Contains raw recursive info extracted from papers
 - `readable_csv` csv containing only bullet points of the extracted info easily readable by human

#### Confidence score for fact statements
 


