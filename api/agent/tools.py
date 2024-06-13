from langchain_core.tools import tool
import csv
from ..data.data import Requisition_data, Suppliers_info
import pathlib

hey = pathlib.Path
# print(hey)

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
def get_supplier_details(search_term):
  """
  Searches supplier information by supplier ID or name (case-insensitive).

  Args:
      supplier_info (dict): Dictionary containing supplier data.
      search_term (str): Supplier ID or name to search for.

  Returns:
      dict: Supplier details dictionary if found, otherwise empty dictionary.
  """
  supplier_info = Suppliers_info

  # Improve data by converting numeric values to floats (e.g., on-time delivery rate)
  for supplier, data in supplier_info.items():
    for key, value in data["performance_data"].items():
      if isinstance(value, str) and value.replace('.', '', 1).isdigit():
        supplier_info[supplier]["performance_data"][key] = float(value)

  # Search by ID or name (case-insensitive)
  search_term = search_term.lower()
  for supplier_id, supplier_data in supplier_info.items():
    if (supplier_id.lower() == search_term or
        supplier_data["supplier_name"].lower().startswith(search_term)):
      return supplier_data
  return 'The supplier with the detail {search_term} doesnt exist!!!'

@tool("procurement_details", return_direct=False)
def get_procurement_data(filename='..data/procurement_data.csv', search_term='', search_column="agency"):
  """
  Searches procurement data in a CSV file based on a search term and column.

  Args:
      filename (str): Path to the CSV file containing procurement data.
      search_term (str): The term to search for in the specified column.
      search_column (str, optional): The column to search in (defaults to "agency").

  Returns:
      list: List of dictionaries containing matching procurement data rows.
  """

  results = []
  with open(filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    # Search by the specified column (case-insensitive)
    search_term = search_term.lower()
    for row in reader:
      if row[search_column].lower() == search_term:
        results.append(row)

  return results

