from datetime import datetime


class Transaction:
    def __init__(self, document_id, payment_id, amount, date, vendor_name, vendor_address):
        self.document_id = document_id
        self.payment_id = payment_id
        self.amount = amount
        # self.date = datetime.strptime(date, "%Y-%m-%d").date()
        self.date = date
        self.vendor_name = vendor_name
        self.vendor_address = vendor_address
        self.validated = False

    def validate(self):
        self.validated = True

    def print_data(self):
        print(', '.join([str(self.document_id), str(self.payment_id), str(self.amount), str(self.date),
                         str(self.vendor_name), str(self.vendor_address), str(self.validated)]))
