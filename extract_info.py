import os
import PyPDF2
import openai
import csv
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--downloaded_pdfs_directory",
    default="./downloaded_pdfs",
    type=str,
)

parser.add_argument(
    "--extracted_info_csv",
    default="./downloaded_pdfs/results.csv",
    type=str,
)

parser.add_argument(
    "--open_api_key",
    default="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",
    type=str,
)

parser.add_argument(
    "--readable_csv",
    default="./downloaded_pdfs/output.csv",
    type=str,
)


def convert_to_bullet_points(paragraph):
    # Split the paragraph into sentences
    sentences = paragraph.split(". ")

    # Add bullet points to each sentence
    bullet_points = ["\u2022 " + sentence for sentence in sentences]

    # Join the bullet points to form a new paragraph
    new_paragraph = "\n".join(bullet_points)

    return new_paragraph


def convert_csv_to_bullet_points(input_file, output_file):
    with open(input_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # Read the header row

        # Create a dictionary to store the modified data
        modified_data = {header: [] for header in headers}

        for row in reader:
            for i, value in enumerate(row):
                modified_value = convert_to_bullet_points(value)
                modified_data[headers[i]].append(modified_value)

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)  # Write the header row

        # Write the modified data
        for i in range(len(modified_data[headers[0]])):
            row = [modified_data[header][i] for header in headers]
            writer.writerow(row)


if __name__ == "__main__":

    args = parser.parse_args()

    openai.api_key = args.open_api_key
    directory = args.downloaded_pdfs_directory

    # Define the CSV file path
    csv_file = args.extracted_info_csv
    is_first_step = True
    file_paths = []

    # Iterate over all files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    for path in file_paths:
        print(path)
        point_and_pathway = ""
        company = ""
        drug_and_dieseas = ""

        pdf_file_path = path
        pdf_file = open(pdf_file_path, "rb")
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        for page_num in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page_num].extract_text().lower()

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant and vet analyst.",
                    },
                    {
                        "role": "user",
                        "content": f"What is the company or research group doing this research? {page_text}",
                    },
                ],
            )
            company_response = response["choices"][0]["message"]["content"]
            company += company_response + "\n"

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant and vet analyst.",
                    },
                    {
                        "role": "user",
                        "content": f"What is the name of the drug in this research and what is the dieseas that it is being used for? {page_text}",
                    },
                ],
            )
            drug_and_dieseas_response = response["choices"][0]["message"]["content"]
            drug_and_dieseas += drug_and_dieseas_response + "\n"

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant and vet analyst.",
                    },
                    {
                        "role": "user",
                        "content": f"What is the biological pathway for this drug and what is the exact point that they are targetting with this research?: {page_text}",
                    },
                ],
            )
            pathway_and_point_response = response["choices"][0]["message"]["content"]

            point_and_pathway += pathway_and_point_response + "\n"

        pdf_summary_file = pdf_file_path.replace(
            os.path.splitext(pdf_file_path)[1], "_summary.txt"
        )
        with open(pdf_summary_file, "w+") as file:
            file.write("Company_or_research_agency:\n")
            file.write(company)
            file.write("\nDrug_and_dieseas:\n")
            file.write(drug_and_dieseas)
            file.write("\nPoint_and_pathway:\n")
            file.write(point_and_pathway)

        pdf_file.close()

        query_dict = {
            "Company_or_research_agency": company,
            "Drug_and_dieseas": drug_and_dieseas,
            "Point_and_pathway": point_and_pathway,
        }

        answer_dict = {}

        for key, value in query_dict.items():
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant.",
                    },
                    {
                        "role": "user",
                        "content": f"This text contains either of these: Name entity of company or research organization, Name of drug and target dieseas, Drug pathway and point. Your job is to figure out which one of these is contained in the text and give out the specific desired output from that for company name, drug and dieseas, pathway and point. Try to be specific with this information.{value}",
                    },
                ],
            )
            answer_dict[key] = response["choices"][0]["message"]["content"]

        # Finally put it into a string of form ""Company x is developing y type of drug, targeting z point in w biological pathway for v dieseas"". Here x should be company name, y name of drug,z point in biological pathway, w biological pathway, v dieseas.

        file_name = os.path.basename(path)
        file_name = os.path.splitext(file_name)[0]
        answer_dict["paper"] = file_name

        # Open the CSV file in append mode and write the dictionary values
        with open(csv_file, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=answer_dict.keys())

            # Write the values as a new row
            writer.writerow(answer_dict)

    # Example usage
    input_file = args.extracted_info_csv
    output_file = args.readable_csv

    convert_csv_to_bullet_points(input_file, output_file)
