from app.services.email_service import read_emails

from app.services.extraction_service import (
    extract_employee_data
)

from app.services.db_service import (
    insert_mail_data
)

mails = read_emails()

for mail in mails:

    extracted = extract_employee_data(mail)

    for row in extracted:

        insert_mail_data(row)

        print("Inserted:")

        print(row)