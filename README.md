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
 python3 extract_info.py --download_pdfs_directory --extracted_info_csv --open_api_key --readable_csv
 ```
 where the arguments:
 - `download_pdfs_directory` refers to the path where the papers are stored
 - `extracted_info_csv` Contains raw recursive info extracted from papers
 - `readable_csv` csv containing only bullet points of the extracted info easily readable by human

#### Confidence score for fact statements
 ```bash
 python3 score.py --search_term --papers_json --trials_csv --save --open_api_key --question
```
 where the arguments:
 - `search_term` refers to the dieseas who's published article data, clinical trials data needs to be pulled up using pubmed API (abstracts only for now, ideally it should work with extracted information by extract_info.py) and ClinicalTrialsGov.py respectively
 - `papers_json` json in which concatinated abstract info will be stored
 - `trials_csv` csv in which trials data information will be stored
 - `save` bool flag to save above two data
 - `question` Question or statement who's confidence score is to be checked with respect to the paper and clinical extracted information

#### Setting up vector database with ChatGPT
Create a virtual env and install the dependencies in requirements.txt (vector_db folder). start the app by:  
 ```bash
 uvicorn main:app --host 0.0.0.0 --port 8080
 ```
 The app should be online and the query can be raised to the app in the following format:
  ```bash
 curl --location "http://0.0.0.0/query/<question>"
 ```

Repository under progress :)



