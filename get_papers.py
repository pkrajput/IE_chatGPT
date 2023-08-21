import pandas as pd
import arxiv
import os
import requests
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--download_directory",
    default='/home/prateek/sk_courses/IE_chatGPT/downloaded_pdfs',
    type=str,
)

parser.add_argument(
    "--num_papers",
    default=300,
    type=int,
)

if __name__ == "__main__":

    args = parser.parse_args()
    topic = input("Enter the topic you need to search for : ")
    
    search = arxiv.Search(
    query = topic,
    max_results = args.num_papers,
    sort_by = arxiv.SortCriterion.SubmittedDate,
    sort_order = arxiv.SortOrder.Descending
    )
    
    all_data = []
    for result in search.results():
        temp = ["","","","",""]
        temp[0] = result.title
        temp[1] = result.published
        temp[2] = result.entry_id
        temp[3] = result.summary
        temp[4] = result.pdf_url
        all_data.append(temp)
    column_names = ['Title','Date','Id','Summary','URL']
    df = pd.DataFrame(all_data, columns=column_names)

    print("Number of papers extracted : ",df.shape[0])

    url_column = 'URL'
    title_column = 'Title'
    download_directory = args.download_directory

    # Create the download directory if it doesn't exist
    os.makedirs(download_directory, exist_ok=True)
    # Iterate through the URLs in the DataFrame
    for index, row in df.iterrows():
        pdf_url = row[url_column]
        response = requests.get(pdf_url)
        if response.status_code == 200:
            title = row[title_column]
            # Create a valid filename by removing invalid characters
            title_for_filename = "".join(x if x.isalnum() or x in (' ', '-') else '_' for x in title)
            filename = os.path.join(download_directory, f"{title_for_filename}.pdf")
            # Save the PDF to the specified directory
            with open(filename, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded: {pdf_url} -> {filename}")
        else:
            print(f"Failed to download: {pdf_url}")
            
    print("Download completed.")

