import os
import csv
import base64

from openai import OpenAI
from pathlib import Path
import json


from io import BytesIO

from pdf2image import convert_from_path
from pprint import pprint

import pandas as pd 

def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)


def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def encode_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")


def extract_info_from_pdf(client, images) -> dict:
    all_info = {}
    extract_cols = ["Pay Period", "Check Date", "Gross Pay Current and YTD", "Taxable Wages Current and YTD", "Check Amount Current and YTD"]
    for i, image in enumerate(images):
        encoded_image = encode_image(image)
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract the following information from this paystub image: {', '.join(extract_cols)}. Respond with only these values in a JSON format.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        # Parse the JSON response
        pprint(response.choices[0].message.content)
        page_info = json.loads(response.choices[0].message.content)
        all_info.update(page_info)

    return all_info


def main():
    # pdf_directory = "path/to/your/pdf/directory"  # Replace with the actual path
    output_csv = "output.csv"

    # Initialize OpenAI client
    client = OpenAI(
        api_key=os.environ["OPENAI_KEY"]
    )  # Replace with your actual API key
    print(client)
    # pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

    pdf_files = list(
        Path("/Users/priyesh.rughani/Downloads").glob("Payslip_300000002536654*.pdf")
    )

    data = []
    for pdf_file in pdf_files:
        pdf_content = convert_pdf_to_images(pdf_file)
        info = extract_info_from_pdf(client, pdf_content)
        data.append(info)
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    


    # with open(output_csv, "w", newline="") as csvfile:
        # fieldnames = [
        #     "Pay Period",
        #     "Check Date",
        #     "Gross Pay YTD",
        #     "Gross Pay Current",
        #     "Taxable Wages Current",
        #     "Taxable Wages YTD",
        #     "Check Amount Current",
        #     "Check Amount YTD",
        # ]
        # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # writer.writeheader()

        # for pdf_file in pdf_files:
        #     # pdf_path = os.path.join(pdf_directory, pdf_file)
        #     pdf_content = convert_pdf_to_images(pdf_file)
        #     info = extract_info_from_pdf(client, pdf_content)
        #     writer.writerow(info)
        #     # break

    print(f"CSV file '{output_csv}' has been created with the extracted information.")


if __name__ == "__main__":
    main()
