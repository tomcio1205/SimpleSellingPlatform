from DBConnection.DatabaseConnection import PostgresConnection
from Config.DBConfig import database_parameters
from Report.GenerateReport import GeneratePDFReport
import json
import os
import sys
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE

REPORT_NAME = 'daily_report'
MAIL_FROM = 'tomekrajzer@gmail.com'
MAIL_SUBJECT = 'Daily report'
MAIL_BODY = 'Example body'


def execute_query(query, args=()):
    db_param = database_parameters()
    with PostgresConnection(db_param, query, args) as ps:
        return ps


def get_data():
    email_to_send = []
    all_staff = execute_query("select e.email from users e" \
                              " left join users_type ut on ut.id=e.user_type_id" \
                              " where ut.type = 'staff' ")

    all_records = execute_query("SELECT o.id, o.total_price, o.create_time, p.title, od.product_counts " \
                                "FROM orders o " \
                                "left join order_details od on od.order_id=o.id " \
                                "left join products p on od.product_id=p.id " \
                                "WHERE o.create_time > current_date - interval '1' day")

    for email in json.loads(all_staff):
        email_to_send.append(email['email'])

    all_products_quant = 0
    money = 0
    product_counts = {}
    product = {}
    for item in json.loads(all_records):
        if item['title'] in product_counts:
            product_counts[item['title']] += item['product_counts']
            all_products_quant += item['product_counts']
        else:
            product_counts[item['title']] = 0
            product_counts[item['title']] += item['product_counts']
            money += item['total_price']
            all_products_quant += item['product_counts']

    maxval = max(product_counts.values())
    keys = [k for k, v in product_counts.items() if v == maxval][0]
    product['title'] = keys
    product['quantity'] = maxval
    GeneratePDFReport(money, all_products_quant, REPORT_NAME, product).create_report()
    send_mail(email_to_send)


def send_mail(emails):
    FROM = MAIL_FROM
    TO = emails

    username = 'tomekrajzer@gmail.com'
    password = 'xxxxxxxx'

    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = MAIL_SUBJECT
    outer['To'] = COMMASPACE.join(TO)
    outer['From'] = MAIL_FROM
    outer.preamble = 'PREAMBLE.\n'

    # List of attachments
    report_path = "{}/temp/{}.pdf".format(os.getcwd(), REPORT_NAME)
    attachments = [report_path]

    # Add the attachments to the message
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)
        except:
            print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
            raise

    composed = outer.as_string()

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(FROM, TO, composed)
        server.close()
        print("successfully sent the mail")
    except:
        print("failed to send mail")


if __name__ == '__main__':
    get_data()
