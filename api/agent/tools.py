from langchain_core.tools import tool
import csv
from ..data.data import Requisition_data, Suppliers_info
import pathlib
from ..data.get_from_db import get_supplier_data
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import find_dotenv, load_dotenv
import logging
import re
from datetime import datetime


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

def determine_data_type(identifiers):
    """
    Determines the data type of the provided identifiers.
    Args:
        identifiers (list): A list of report identifiers.
    Returns:
        str: The data type of the identifiers ("ID", "name", "invoice_id", "supplier_id" or "date").
    """
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    for identifier in identifiers:
        if identifier.startswith("REP") and len(identifier) == 13:
            return "ID"
        elif re.match(date_pattern, identifier):
            return "date"
        elif identifier.startswith("INV"):
            return "invoice_id"
        elif identifier.startswith("SUP"):
            return "supplier_id"
    return "name"

# my custom tools
@tool("requisition_details", return_direct=False)
def get_requisition_details(requisition_number):
  """
  Simulates API call to retrieve requisition details and status.

  Args:
      requisition_number (str): Unique identifier for the requisition.

  Returns:
      dict: Dictionary containing requisition details and status. 
             Empty dictionary if requisition not found.
  """

  if requisition_number in Requisition_data:
    return Requisition_data[requisition_number]
  else:
    return 'Details of this requisition was not found'


@tool("suppliers_details", return_direct=False)
def get_supplier_data(identifiers, data_type=None):
    """
    Retrieves supplier data from the database based on a list of supplier IDs or supplier names,
    or a single supplier ID or supplier name (which may contain commas).
    Args:
        identifiers (list or str): A list of supplier IDs or supplier names, or a single supplier ID or supplier name.
        data_type (str, optional): The type of identifier provided. Can be "supplier_id" or "name". If not provided, the function will attempt to determine the data type automatically.
        connection (sqlalchemy.engine.Connection): The SQLAlchemy connection object.
    Returns:
        A list of dictionaries containing the retrieved supplier data, or an empty list if no matching suppliers are found.
    """
    connection = engine.connect()
    try:
        if not identifiers:
            return []
        if isinstance(identifiers, str):
            # If a single value is provided, split it on commas and create a list
            identifiers = [value.strip() for value in identifiers.split(',')]

        if data_type is None:
            # Attempt to determine the data type automatically
            data_type = determine_data_type(identifiers)

        conditions = []
        params = {}

        if data_type == "supplier_id":
            conditions.append("supplier_id = ANY(:supplier_ids)")
            params["supplier_ids"] = identifiers
        elif data_type == "name":
            conditions.append("supplier_name = ANY(:supplier_names)")
            params["supplier_names"] = identifiers
        else:
            return 'Invalid data type provided'

        if not conditions:
            return 'No valid identifier for the supplier provided'

        query = text("""
            SELECT supplier_id, supplier_name, contact_info, total_orders, total_spent, average_rating, on_time_delivery_rate
            FROM finance.suppliers
            WHERE {}
        """.format(" OR ".join(conditions)))

        result = connection.execute(query, params)
        supplier_data = []
        for row in result:
            supplier_dict = {
                "supplier_id": row.supplier_id,
                "supplier_name": row.supplier_name,
                "contact_info": row.contact_info,
                "total_orders": row.total_orders,
                "total_spent": float(row.total_spent),
                "average_rating": float(row.average_rating) if row.average_rating is not None else None,
                "on_time_delivery_rate": float(row.on_time_delivery_rate) if row.on_time_delivery_rate is not None else None
            }
            supplier_data.append(supplier_dict)
        if not supplier_data:
            return f'No record found for the suppliers: {identifiers}'
        return supplier_data
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

@tool("procurement_details", return_direct=False)
def get_procurement_data(identifiers, data_type=None):
    """
    Retrieves procurement report data from the database based on a list of report IDs (ID format: REP0JOJJGKRGZ), report names, or generated dates (date format: Year-Month-Day i.e 2023-06-13),
    or a single report ID, report name, or generated date (which may contain commas).
    Args:
        report_identifiers (list or str): A list of report IDs , report names, or generated dates , or a single report ID, report name, or generated date.
        data_type (str, optional): The type of identifier provided. Can be "ID", "name", or "date". If not provided, the function will attempt to determine the data type automatically.
        connection (sqlalchemy.engine.Connection): The SQLAlchemy connection object.
    Returns:
        A list of dictionaries containing the retrieved procurement report data, or an empty list if no matching reports are found.
    """
    connection = engine.connect()
    try:
        if not identifiers:
            return []
        if isinstance(identifiers, str):
            # If a single value is provided, split it on commas and create a list
            identifiers = [value.strip() for value in identifiers.split(',')]

        if data_type is None:
            # Attempt to determine the data type automatically
            data_type = determine_data_type(identifiers)

        conditions = []
        params = {}

        if data_type == "ID":
            conditions.append("report_id = ANY(:report_ids)")
            params["report_ids"] = identifiers
        elif data_type == "name":
            conditions.append("report_name = ANY(:report_names)")
            params["report_names"] = identifiers
        elif data_type == "date":
            report_dates = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in identifiers]
            conditions.append("generated_date = ANY(:report_dates)")
            params["report_dates"] = report_dates
        else:
            return 'Invalid data type provided'

        if not conditions:
            return 'No valid identifiers provided'

        query = text("""
            SELECT report_id, report_name, generated_date, total_orders, total_spent, top_suppliers
            FROM finance.procurement_reports
            WHERE {}
        """.format(" OR ".join(conditions)))

        result = connection.execute(query, params)
        report_data = []
        for row in result:
            report_dict = {
                "report_id": row.report_id,
                "report_name": row.report_name,
                "generated_date": str(row.generated_date),
                "total_orders": row.total_orders,
                "total_spent": float(row.total_spent),
                "top_suppliers": row.top_suppliers
            }
            report_data.append(report_dict)
        if not report_data:
            return 'No record found for procurement reports'
        return report_data
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

@tool("invoice_details", return_direct=False)
def get_invoice_data(identifiers, data_type=None):
    """
    Retrieves invoice data from the database based on a list of invoice IDs or supplier IDs,
    or a single invoice ID or supplier ID (which may contain commas).
    Args:
        identifiers (list or str): A list of invoice IDs or supplier IDs, or a single invoice ID or supplier ID.
        data_type (str, optional): The type of identifier provided. Can be "invoice_id" or "supplier_id". If not provided, the function will attempt to determine the data type automatically.
        connection (sqlalchemy.engine.Connection): The SQLAlchemy connection object.
    Returns:
        A list of dictionaries containing the retrieved invoice data, or an empty list if no matching invoices are found. 
    """
    connection = engine.connect()
    try:
        if not identifiers:
            return []
        if isinstance(identifiers, str):
            # If a single value is provided, split it on commas and create a list
            identifiers = [value.strip() for value in identifiers.split(',')]

        if data_type is None:
            # Attempt to determine the data type automatically
            data_type = determine_data_type(identifiers)

        conditions = []
        params = {}

        if data_type == "invoice_id":
            conditions.append("invoice_id = ANY(:invoice_ids)")
            params["invoice_ids"] = identifiers
        elif data_type == "supplier_id":
            conditions.append("supplier_id = ANY(:supplier_ids)")
            params["supplier_ids"] = identifiers
        else:
            return 'Invalid data type provided'

        if not conditions:
            return 'No valid identifiers provided'

        query = text("""
            SELECT invoice_id, purchase_order_id, supplier_id, invoice_date, due_date, amount_due, status, payment_date, payment_method
            FROM finance.invoices
            WHERE {}
        """.format(" OR ".join(conditions)))

        result = connection.execute(query, params)
        invoice_data = []
        for row in result:
            invoice_dict = {
                "invoice_id": row.invoice_id,
                "purchase_order_id": row.purchase_order_id,
                "supplier_id": row.supplier_id,
                "invoice_date": str(row.invoice_date),
                "due_date": str(row.due_date),
                "amount_due": float(row.amount_due),
                "status": row.status,
                "payment_date": str(row.payment_date) if row.payment_date else None,
                "payment_method": row.payment_method
            }
            invoice_data.append(invoice_dict)
        if not invoice_data:
            return 'No record found for invoices'
        return invoice_data
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()
