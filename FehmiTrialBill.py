from Receipt import Receipt
from Transaction import Transaction
import re
import os
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
pattern = [
    {"SHAPE": "dd"}, {"ORTH": "/"}, {"SHAPE": "dd"}, {"ORTH": "/"}, {"SHAPE": "dddd"}
]
matcher.add("DATE", [pattern])


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Iterate through the named entities and check if they are of type 'GPE' or 'LOC'
def find_addy(text):
    doc = nlp(text)
    for match_id, start, end in matcher(doc):
        span = doc[start:end]
    for ent in doc.ents:
        if ent.label_ == "GPE" or ent.label_ == "LOC":
            location = str(ent)
            address = text[ent.start: text.find(location) + len(location)].strip()
            name = text[:ent.start].strip()
            return name, address


all_lines_raw = []
with open('Users.csv', 'r', newline='') as f:
    for item in f:
        split_string = re.split(r'[,"]+', item)
        all_lines_raw.append(split_string)

    all_lines_clean = []
    for line in all_lines_raw:
        address = re.sub('"', '', " ".join(line[5:]).strip('\n'))
        full_line = line[:5] + [address]
        # print(full_line)
        all_lines_clean.append(full_line)

    all_transactions = {}
    for line in all_lines_clean:
        new_transaction = Transaction(line[0], line[1], line[2], line[3], line[4], line[5])
        all_transactions[line[0]] = new_transaction

all_transactions['00d0403711886'].print_data()

directory = 'ocr/'
vendor_name = ""
shop_address = ""
date = 0

patterns = [
    r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.]((19|20)\d\d)',  # dd-mm-yyyy
    r'(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.]((19|20)\d\d)',  # mm-dd-yyyy
    r'((19|20)\d\d)[- /.](0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])',  # yyyy-dd-mm
    r'((19|20)\d\d)[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])',  # yyyy-mm-dd
    r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](\d\d)',  # dd-mm-yy
    r'(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](\d\d)'  # mm-dd-yy
]


def get_date(text):
    possible_dates = set()
    for pat in patterns:
        for match in re.finditer(pat, text):
            possible_dates.add(match.group())
    return possible_dates.pop()


recs = []
for filename in os.listdir(directory):
    if filename == "00d0403711886.csv":
        with open(os.path.join(directory, filename), 'r') as file:
            all_text = " "
            all_total_coordinates = []
            everything_after = []
            total_yet = False

            for line in file:
                actual_receipt_text_split = line.split(",")[8:]
                actual_receipt_text = " ".join(actual_receipt_text_split).strip('\n')
                line = ", ".join(line.split(",")).strip('\n')
                all_text += actual_receipt_text + " "

                if "total" in actual_receipt_text.lower():
                    # print(line)
                    all_total_coordinates.append(line.split(","))
                    total_yet = True

                if total_yet:
                    if line[:8] not in all_total_coordinates:
                        line = line.split(",")
                        if is_number(line[8]):
                            # print(line)
                            # To add everything that comes after total and nothing before
                            everything_after.append(line)

        date = get_date(all_text)
        vendor_name, shop_address = find_addy(all_text)

        recs.append(Receipt(filename, "0", date, vendor_name, shop_address))


def box_alg(a, b):
    y1 = .5 * (float(a[7]) + float(a[1]))
    y2 = .5 * (float(b[7]) + float(b[1]))
    return abs(y2 - y1)


matching_totals = []
for box1 in all_total_coordinates:
    for box2 in everything_after:
        diff = box_alg(box1[:8], box2[:8])
        if diff == 0 or diff < 10:
            print(diff)
            print(box1[8], box2[8])
            matching_totals.append([box1[8], box2[8]])


def find_actual_total(data):
    result = 0
    for pair in data:
        text = pair[0].lower()
        print(text)
        total = pair[1]
        if "total" in text:
            if "inc" in text:
                result = total
            if "including" in text:
                result = total
            if "payable" in text:
                result = total
            if "after" in text:
                result = total
            if "gst" in text:
                result = total
            if "net" in text:
                result = total
    return result


print(find_actual_total(matching_totals))
