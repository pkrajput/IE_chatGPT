from pymed import PubMed
import pandas as pd
import argparse
from ClinicalTrialsGov import get_trials
import PyPDF2
import openai
import os
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch
import time
import warnings

pubmed = PubMed(tool="PubMedSearcher", email="gunner.hardy@gmail.com")
warnings.filterwarnings("ignore", category=DeprecationWarning)

parser = argparse.ArgumentParser()

parser.add_argument(
    "--search_term",
    default=None,
    type=str,
)

parser.add_argument(
    "--papers_json",
    default="./downloaded_pdfs/pub.json",
    type=str,
)

parser.add_argument(
    "--trials_csv",
    default="./downloaded_pdfs/trials.csv",
    type=str,
)

parser.add_argument(
    "--save",
    default=False,
    type=bool,
)

parser.add_argument(
    "--openai_api_key",
    default='API_KEY',
    type=str,
)

parser.add_argument(
    "--question",
    default="Therapy suggested is potentially very proimising",
    type=str,
)

# Function to get the confidence score for the question
def get_confidence_score(question, paragraph):
    inputs = tokenizer(question, paragraph, return_tensors="pt", truncation=True)
    inputs.to(device)  # Move inputs to GPU (if available)

    # Enable model to be in evaluation mode
    model.eval()

    with torch.no_grad():
        start_time = time.time()
        logits = model(**inputs).logits
        probabilities = logits.softmax(dim=1)
        inference_time = time.time() - start_time
        confidence_score = probabilities[:, 1].item() * 100

    return confidence_score, inference_time


if __name__ == "__main__":

    args = parser.parse_args()
    openai.api_key = args.openai_api_key
    search_term = args.search_term

    results = pubmed.query(search_term, max_results=5)
    articleList = []
    articleInfo = []
    abstracts = []

    for article in results:
        articleDict = article.toDict()
        articleList.append(articleDict)

    # Generate list of dict records which will hold all article details that could be fetched from the PUBMED API
    for article in articleList:
        # Sometimes article['pubmed_id'] contains a list separated with a comma - take the first pubmedId in that list - that's the article pubmedId
        pubmedId = article["pubmed_id"].partition("\n")[0]
        # Append article info to the dictionary
        articleInfo.append(
            {
                "pubmed_id": pubmedId,
                "title": article["title"],
                "keywords": article["keywords"],
                "journal": article["journal"],
                "abstract": article["abstract"],
                "conclusions": article["conclusions"],
                "methods": article["methods"],
                "results": article["results"],
                "copyrights": article["copyrights"],
                "doi": article["doi"],
                "publication_date": article["publication_date"],
                "authors": article["authors"],
            }
        )
        
        if type(article["abstract"]) == str:
        	abstracts.append(article["abstract"])
         
         
    articlesPD = pd.DataFrame.from_dict(articleInfo)

    # Convert DataFrame to JSON
    json_data = articlesPD.to_json(orient="records", indent=4)

    gene_therapy_trials = get_trials(args.search_term)
    df_gt = gene_therapy_trials.astype(str)
 
    if args.save == True:
        # Write JSON data to a file
        with open(args.papers_json, "w") as json_file:
            json_file.write(json_data)

        # Write the DataFrame to a .csv file
        gene_therapy_trials.to_csv(args.trials_csv, sep="\t", index=False)
    
    text = " ".join(abstracts)
    response = openai.ChatCompletion.create(
	model="gpt-3.5-turbo",
	messages=[
		{"role": "system", "content": "You are a helpful research assistant."},
		{"role": "user", "content": f"What are the claims of this text? {text}"},
	],
	)
    focus_response = response["choices"][0]["message"]["content"]
    
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    confidence_score, inference_time = get_confidence_score(args.question, focus_response)
    print("Confidence Score based on recent research: ", confidence_score)
    print("Inference Time: {:.2f} seconds".format(inference_time)) 
    
    response = openai.ChatCompletion.create(
	model="gpt-3.5-turbo",
	messages=[
		{"role": "system", "content": "You are a helpful research assistant."},
		{"role": "user", "content": f"Get a summary of these clinical trials {df_gt}"},
	],
	)
    focus_response = response["choices"][0]["message"]["content"]
    
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    confidence_score, inference_time = get_confidence_score(args.question, focus_response)
    print("Confidence Score based on clinical trials: ", confidence_score)
    print("Inference Time: {:.2f} seconds".format(inference_time)) 
    
    
		
    
