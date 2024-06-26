from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import find_dotenv, load_dotenv
import logging
import csv
import json
from icecream import ic
import json
import random
import string
from faker import Faker
from datetime import date

fake = Faker()

load_dotenv(find_dotenv())


def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not found.")
    return value
 
POSTGRES_DB_N = get_env_variable("POSTGRES_DB_N")
POSTGRES_USER_N = get_env_variable("POSTGRES_USER_N")
POSTGRES_PASSWORD_N = get_env_variable("POSTGRES_PASSWORD_N")
DB_HOST_N = get_env_variable("DB_HOST_N")
DB_PORT_N = get_env_variable("DB_PORT_N")

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# SQLAlchemy engine setup
engine = create_engine(f"postgresql+psycopg://{POSTGRES_USER_N}:{POSTGRES_PASSWORD_N}@{DB_HOST_N}:{DB_PORT_N}/{POSTGRES_DB_N}")
Session = sessionmaker(bind=engine)
db_url = f"postgresql+psycopg://{POSTGRES_USER_N}:{POSTGRES_PASSWORD_N}@{DB_HOST_N}:{DB_PORT_N}/{POSTGRES_DB_N}"
connection = engine.connect()

    
def close_connection():
    connection.close()

def handle_error(e):
        # Log the error or handle it as needed
        return f"An error occurred: {e}"

# Database connection parameters


# Function to create tables
def create_tables():
    
    try:
         # Create a schema
        schema = text("""CREATE SCHEMA IF NOT EXISTS finance;""")
        
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS finance.purchase_orders (
                purchase_order_id VARCHAR(20) PRIMARY KEY,
                purchase_requisition_id VARCHAR(20),
                status VARCHAR(20),
                created_date DATE,
                approved_date DATE,
                supplier_id VARCHAR(20),
                items JSONB
            );
          
            CREATE TABLE IF NOT EXISTS finance.invoices (
                invoice_id VARCHAR(20) PRIMARY KEY,
                purchase_order_id VARCHAR(20),
                supplier_id VARCHAR(20),
                invoice_date DATE,
                due_date DATE,
                amount_due NUMERIC,
                status VARCHAR(20),
                payment_date DATE,
                payment_method VARCHAR(20)
            );
           
            CREATE TABLE IF NOT EXISTS finance.procurement_reports (
                report_id VARCHAR(20) PRIMARY KEY,
                report_name VARCHAR(50),
                generated_date DATE,
                total_orders INTEGER,
                total_spent NUMERIC,
                top_suppliers JSONB
            );
          
            CREATE TABLE IF NOT EXISTS finance.negotiations (
                negotiation_id VARCHAR(20) PRIMARY KEY,
                supplier_id VARCHAR(20),
                purchase_order_id VARCHAR(20),
                initial_offer NUMERIC,
                final_agreement NUMERIC,
                negotiation_date DATE,
                negotiation_status VARCHAR(20)
            );
          
            CREATE TABLE IF NOT EXISTS finance.sourcing (
                sourcing_id VARCHAR(20) PRIMARY KEY,
                sourcing_event VARCHAR(50),
                created_date DATE,
                closing_date DATE,
                status VARCHAR(20),
                bids_received INTEGER,
                selected_supplier_id VARCHAR(20),
                selected_bid_amount NUMERIC
            );
        
            CREATE TABLE IF NOT EXISTS finance.requisitions (
                    requisition_id VARCHAR(20) PRIMARY KEY,
                    created_by VARCHAR(50),
                    created_date DATE,
                    status VARCHAR(50),
                    supplier_name VARCHAR(100),
                    items_requested JSONB,
                    date_sent_rfq DATE,
                    follow_up_sent BOOLEAN,
                    rfq_name VARCHAR(100)
                );
         
            CREATE TABLE IF NOT EXISTS finance.suppliers (
                supplier_id VARCHAR(20) PRIMARY KEY,
                supplier_name VARCHAR(100),
                contact_info JSONB,
                total_orders INTEGER,
                total_spent NUMERIC,
                average_rating NUMERIC,
                on_time_delivery_rate NUMERIC
            );
          
            CREATE TABLE IF NOT EXISTS finance.expense_reports (
                expense_report_id VARCHAR(20) PRIMARY KEY,
                employee_id VARCHAR(20),
                employee_name VARCHAR(50),
                department VARCHAR(50),
                report_date DATE,
                total_amount NUMERIC,
                status VARCHAR(20),
                approved_date DATE,
                expense_items JSONB
            );
        
            CREATE TABLE IF NOT EXISTS finance.budgets (
                budget_id VARCHAR(20) PRIMARY KEY,
                department VARCHAR(50),
                fiscal_year VARCHAR(10),
                total_budget NUMERIC,
                allocated_to_date NUMERIC,
                remaining_budget NUMERIC,
                expenses JSONB
            );
            """
        )

        indexes = text(
        "CREATE INDEX IF NOT EXISTS idx_po_supplier_id ON Finance.purchase_orders (supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_inv_purchase_order_id ON Finance.invoices (purchase_order_id)",
        "CREATE INDEX IF NOT EXISTS idx_inv_supplier_id ON Finance.invoices (supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_neg_supplier_id ON Finance.negotiations (supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_neg_purchase_order_id ON Finance.negotiations (purchase_order_id)",
        "CREATE INDEX IF NOT EXISTS idx_src_supplier_id ON Finance.sourcing (selected_supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_proc_supplier_id ON Finance.procurements (supplier_id)",
        " CREATE INDEX IF NOT EXISTS idx_req_requisition_id ON Finance.requisitions (requisition_id);",
        "CREATE INDEX IF NOT EXISTS idx_exp_employee_id ON Finance.expense_reports (employee_id)",
        "CREATE INDEX IF NOT EXISTS idx_bud_department ON Finance.budgets (department)"
    )

        create_schema = connection.execute(schema)
        create_table = connection.execute(create_table_query)
        create_indexes = connection.execute(indexes)



    except Exception as e:
            error = handle_error(e)
            return error
    # finally:
    #     # Ensure the connection is closed
    #     close_connection()

# Helper functions to generate random data
def random_id(prefix, length=10):
    return prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_date(start_year=2019, end_year=2024):
    datez = fake.date_between(start_date= date(2019, 2, 2) , end_date=date(2024, 12, 31)) #'2019-02-02''2024-12-31'
    # ic(datez)
    return str(datez)

def generate_unique_supplier_names(num_suppliers):
    companies = [fake.company() for _ in range(num_suppliers)]
    return companies

# Function to insert suppliers
def insert_suppliers(num_suppliers):
    suppliers = []
    for _ in range(num_suppliers):
        supplier_id = random_id('SUP')
        supplier_name = fake.company()
        contact_info = {
            'email': fake.email(),
            'phone': fake.phone_number()
        }
        total_orders = random.randint(10, 100)
        total_spent = random.uniform(10000, 100000)
        average_rating = round(random.uniform(1, 5), 1)
        on_time_delivery_rate = round(random.uniform(70, 100), 2)

        supplier_data = {
            'supplier_id': supplier_id,
            'supplier_name': supplier_name,
            'contact_info': json.dumps(contact_info),
            'total_orders': total_orders,
            'total_spent': total_spent,
            'average_rating': average_rating,
            'on_time_delivery_rate': on_time_delivery_rate
        }
        suppliers.append(supplier_data)

    insert_query = text("""
        INSERT INTO finance.suppliers (supplier_id, supplier_name, contact_info, total_orders, total_spent, average_rating, on_time_delivery_rate)
        VALUES (:supplier_id, :supplier_name, :contact_info, :total_orders, :total_spent, :average_rating, :on_time_delivery_rate)
    """)
    connection.execute(insert_query, suppliers)
    connection.commit()

def insert_invoices(num_invoices):
    invoices = []
    for _ in range(num_invoices):
        invoice_id = random_id('INV')
        purchase_order_id = random_id('PO')
        supplier_id = random_id('SUP')
        invoice_date = random_date()
        due_date = random_date()
        amount_due = round(random.uniform(1000, 10000), 2)
        status = random.choice(['Pending', 'Paid', 'Overdue'])
        payment_date = random_date() if status == 'Paid' else None
        payment_method = random.choice(['Credit Card', 'Bank Transfer', 'Cash']) if status == 'Paid' else None

        invoice_data = {
            'invoice_id': invoice_id,
            'purchase_order_id': purchase_order_id,
            'supplier_id': supplier_id,
            'invoice_date': invoice_date,
            'due_date': due_date,
            'amount_due': amount_due,
            'status': status,
            'payment_date': payment_date,
            'payment_method': payment_method
        }
        invoices.append(invoice_data)

    insert_query = text("""
        INSERT INTO Finance.invoices (invoice_id, purchase_order_id, supplier_id, invoice_date, due_date, amount_due, status, payment_date, payment_method)
        VALUES (:invoice_id, :purchase_order_id, :supplier_id, :invoice_date, :due_date, :amount_due, :status, :payment_date, :payment_method)
    """)
    connection.execute(insert_query, invoices)
    connection.commit()

def insert_procurement_reports(num_reports):
    procurement_reports = []
    for _ in range(num_reports):
        report_id = random_id('REP')
        report_name = fake.word()
        generated_date = random_date()
        total_orders = random.randint(10, 100)
        total_spent = round(random.uniform(10000, 100000), 2)
        top_suppliers = [
            {"supplier_id": random_id('SUP'), "total_spent": round(random.uniform(1000, 5000), 2)} for _ in range(3)
        ]

        report_data = {
            'report_id': report_id,
            'report_name': report_name,
            'generated_date': generated_date,
            'total_orders': total_orders,
            'total_spent': total_spent,
            'top_suppliers': json.dumps(top_suppliers)
        }
        procurement_reports.append(report_data)

    insert_query = text("""
        INSERT INTO Finance.procurement_reports (report_id, report_name, generated_date, total_orders, total_spent, top_suppliers)
        VALUES (:report_id, :report_name, :generated_date, :total_orders, :total_spent, :top_suppliers)
    """)
    connection.execute(insert_query, procurement_reports)
    connection.commit()

def insert_negotiations(num_negotiations):
    negotiations = []
    for _ in range(num_negotiations):
        negotiation_id = random_id('NEG')
        supplier_id = random_id('SUP')
        purchase_order_id = random_id('PO')
        initial_offer = round(random.uniform(1000, 5000), 2)
        final_agreement = round(random.uniform(500, 4000), 2)
        negotiation_date = random_date()
        negotiation_status = random.choice(['Successful', 'Failed', 'In Progress'])

        negotiation_data = {
            'negotiation_id': negotiation_id,
            'supplier_id': supplier_id,
            'purchase_order_id': purchase_order_id,
            'initial_offer': initial_offer,
            'final_agreement': final_agreement,
            'negotiation_date': negotiation_date,
            'negotiation_status': negotiation_status
        }
        negotiations.append(negotiation_data)

    insert_query = text("""
        INSERT INTO Finance.negotiations (negotiation_id, supplier_id, purchase_order_id, initial_offer, final_agreement, negotiation_date, negotiation_status)
        VALUES (:negotiation_id, :supplier_id, :purchase_order_id, :initial_offer, :final_agreement, :negotiation_date, :negotiation_status)
    """)
    connection.execute(insert_query, negotiations)
    connection.commit()

def insert_sourcing(num_sourcing):
    sourcing_records = []
    for _ in range(num_sourcing):
        sourcing_id = random_id('SRC')
        sourcing_event = fake.word()
        created_date = random_date()
        closing_date = random_date()
        status = random.choice(['Open', 'Closed', 'Cancelled'])
        bids_received = random.randint(1, 10)
        selected_supplier_id = random_id('SUP') if status == 'Closed' else None
        selected_bid_amount = round(random.uniform(1000, 5000), 2) if selected_supplier_id else None

        sourcing_data = {
            'sourcing_id': sourcing_id,
            'sourcing_event': sourcing_event,
            'created_date': created_date,
            'closing_date': closing_date,
            'status': status,
            'bids_received': bids_received,
            'selected_supplier_id': selected_supplier_id,
            'selected_bid_amount': selected_bid_amount
        }
        sourcing_records.append(sourcing_data)

    insert_query = text("""
        INSERT INTO Finance.sourcing (sourcing_id, sourcing_event, created_date, closing_date, status, bids_received, selected_supplier_id, selected_bid_amount)
        VALUES (:sourcing_id, :sourcing_event, :created_date, :closing_date, :status, :bids_received, :selected_supplier_id, :selected_bid_amount)
    """)
    connection.execute(insert_query, sourcing_records)
    connection.commit()

def insert_expense_reports(num_reports):
    expense_reports = []
    for _ in range(num_reports):
        expense_report_id = random_id('EXP')
        employee_id = random_id('EMP')
        employee_name = fake.name()
        department = fake.word()
        report_date = random_date()
        total_amount = round(random.uniform(100, 1000), 2)
        status = random.choice(['Submitted', 'Approved', 'Rejected'])
        approved_date = random_date() if status == 'Approved' else None
        expense_items = [
            {"item": fake.word(), "amount": round(random.uniform(10, 100), 2)} for _ in range(5)
        ]

        expense_report_data = {
            'expense_report_id': expense_report_id,
            'employee_id': employee_id,
            'employee_name': employee_name,
            'department': department,
            'report_date': report_date,
            'total_amount': total_amount,
            'status': status,
            'approved_date': approved_date,
            'expense_items': json.dumps(expense_items)
        }
        expense_reports.append(expense_report_data)

    insert_query = text("""
        INSERT INTO Finance.expense_reports (expense_report_id, employee_id, employee_name, department, report_date, total_amount, status, approved_date, expense_items)
        VALUES (:expense_report_id, :employee_id, :employee_name, :department, :report_date, :total_amount, :status, :approved_date, :expense_items)
    """)
    connection.execute(insert_query, expense_reports)
    connection.commit()

def insert_budgets(num_budgets):
    budgets = []
    for _ in range(num_budgets):
        budget_id = random_id('BUD')
        department = fake.word()
        fiscal_year = str(fake.year())
        total_budget = round(random.uniform(100000, 1000000), 2)
        allocated_to_date = round(random.uniform(10000, total_budget), 2)
        remaining_budget = total_budget - allocated_to_date
        expenses = [
            {"expense": fake.word(), "amount": round(random.uniform(100, 1000), 2)} for _ in range(5)
        ]

        budget_data = {
            'budget_id': budget_id,
            'department': department,
            'fiscal_year': fiscal_year,
            'total_budget': total_budget,
            'allocated_to_date': allocated_to_date,
            'remaining_budget': remaining_budget,
            'expenses': json.dumps(expenses)
        }
        budgets.append(budget_data)

    insert_query = text("""
        INSERT INTO Finance.budgets (budget_id, department, fiscal_year, total_budget, allocated_to_date, remaining_budget, expenses)
        VALUES (:budget_id, :department, :fiscal_year, :total_budget, :allocated_to_date, :remaining_budget, :expenses)
    """)
    connection.execute(insert_query, budgets)
    connection.commit()

def insert_requisitions(NumRequisitions):
    try:
        requisitions_data = []
        for _ in range(NumRequisitions):
            requisition_id = random_id('REQ')
            created_by = fake.name()
            created_date = random_date()
            status = random.choice(['Awaiting vendor feedback', 'Approved', 'Pending', 'Canclled', 'Completed'])
            supplier_name = fake.company()
            items_requested = [
                {"item": fake.word(), "quantity": random.randint(1, 100)},
                {"item": fake.word(), "quantity": random.randint(1, 100)},
                {"item": fake.word(), "quantity": random.randint(1, 100)},
                {"item": fake.word(), "quantity": random.randint(1, 100)}
            ]
            date_sent_rfq = random_date()
            follow_up_sent = random.choice([True, False])
            rfq_name = fake.catch_phrase()

            requisition_data = {
                'requisition_id': requisition_id,
                'created_by': created_by,
                'created_date': created_date,
                'status': status,
                'supplier_name': supplier_name,
                'items_requested': json.dumps(items_requested),
                'date_sent_rfq': date_sent_rfq,
                'follow_up_sent': follow_up_sent,
                'rfq_name': rfq_name
            }

            requisitions_data.append(requisition_data)

        insert_query = text("""
            INSERT INTO requisitions (requisition_id, created_by, created_date, status, supplier_name, items_requested, date_sent_rfq, follow_up_sent, rfq_name)
            VALUES (:requisition_id, :created_by, :created_date, :status, :supplier_name, :items_requested, :date_sent_rfq, :follow_up_sent, :rfq_name)
        """)

        connection.execute(insert_query, requisitions_data)
        connection.commit()
    except Exception as e:
        print(f"An error occurred in insert_requisitions: {e}")

# Function to insert purchase orders
def insert_purchase_orders(NumPurchaseOrders):
    if NumPurchaseOrders is None:
            return 'NumPurchaseOrders is None'
    try:
        purchase_orders = []
        ic(fake.word())
        for _ in range(NumPurchaseOrders):
            purchase_order_id = random_id('PO')
            purchase_requisition_id = random_id('PR')
            status = random.choice(['Pending', 'Approved', 'Rejected', 'On-hold'])
            created_date = random_date()
            approved_date = random_date() if status == 'Approved' else None
            supplier_id = random_id('SUP')
            items = [
                {"item_id": random_id('IT'), "description": fake.word(), "quantity": random.randint(1, 100), "unit_price": round(random.uniform(10, 1000), 2)} for _ in range(3)
            ]

            purchase_order = {
                'purchase_order_id': purchase_order_id,
                'purchase_requisition_id': purchase_requisition_id,
                'status': status,
                'created_date': created_date,
                'approved_date': approved_date,
                'supplier_id': supplier_id,
                'items': json.dumps(items)
            }
            purchase_orders.append(purchase_order)

      

        insert_query = text("""
            INSERT INTO Finance.purchase_orders (purchase_order_id, purchase_requisition_id, status, created_date, approved_date, supplier_id, items)
            VALUES (:purchase_order_id, :purchase_requisition_id, :status, :created_date, :approved_date, :supplier_id, :items)
        """)
        connection.execute(insert_query, purchase_orders)
        connection.commit()
    except Exception as e:
        print(f"An error occurred in insert_purchase_orders:: {e}")

# Function to get all supplier IDs
def get_all_supplier_ids():
    try:
        insert_query = text("SELECT supplier_id FROM suppliers")
        result = connection.execute(insert_query)
        supplier_ids = [row[0] for row in result.fetchall()]
        return supplier_ids
    except Exception as e:
            handle_error(e)
            return []
    

def get_all_purchase_order_ids():
    try:
        insert_query = text("SELECT purchase_order_id FROM purchase_orders")
        result = connection.execute(insert_query)
        purchase_order_ids = [row[0] for row in result.fetchall()]
        connection.execute(insert_query)
        connection.commit()
        return purchase_order_ids
    except Exception as e:
            handle_error(e)
            return []




def populate_table(num_records: int = 200):

    connection = engine.connect()

    try:
        # insert_negotiations(num_records) #done
        # insert_sourcing(num_records) #done
        # insert_procurement_reports(num_records) #done
        # insert_expense_reports(num_records) #done
        # insert_budgets(num_records) #done
        # insert_invoices(num_records) #done
        # insert_purchase_orders(num_records) #done

        insert_suppliers(num_records) #done

        # insert_requisitions(num_records)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()


    return "Fake data inserted successfully."