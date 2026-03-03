import pdfplumber
import re
from datetime import datetime


def parse_jaypee_bill(file_path):
    data = {}

    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    lines = full_text.split("\n")

    # -----------------------------
    # 1️⃣ Extract Invoice Period
    # -----------------------------
    if "Invoice Period" in full_text:

        dates = re.findall(r"\d{2}-[A-Za-z]{3}-\d{4}", full_text)

        if dates:
            first_date = dates[0]
            date_obj = datetime.strptime(first_date, "%d-%b-%Y")
            data["month"] = date_obj.month
            data["year"] = date_obj.year
        else:
            data["month"] = None
            data["year"] = None

    # -----------------------------
    # Extract Grid Electricity Data
    # -----------------------------
    for i, line in enumerate(lines):

        if "Grid Electricity" in line:

            combined_line = line

            if i + 1 < len(lines):
                combined_line += " " + lines[i + 1]
            if i + 2 < len(lines):
                combined_line += " " + lines[i + 2]

            numbers = re.findall(r"[\d,]+\.\d+", combined_line)

            numbers = [float(num.replace(",", "")) for num in numbers]

            if len(numbers) >= 6:
                data["units_consumed"] = float(numbers[2])
                data["energy_charges"] = float(numbers[3])
                data["fixed_charges"] = float(numbers[4])
                data["ed_surcharge"] = float(numbers[5])

                if len(numbers) > 6:
                    data["total_grid_amount"] = float(numbers[6])
                else:
                    data["total_grid_amount"] = None

            break

    return data