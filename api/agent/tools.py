from langchain_core.tools import tool
import random
from ..data.data import Requisition_data, Suppliers_info, people


# my custom tools
@tool("lower_case", return_direct=False)
def to_lower_case(input:str) -> str:
  """Returns the input as all lower case."""
  return input.lower()

@tool("random_number", return_direct=False)
def random_number_maker(input:str) -> str:
    """Returns a random number between 0-100. input the word 'random'"""
    return random.randint(0, 100)


@tool("staff_details", return_direct=False)
def find_the_staff(name:str):
    """Returns a staff detail based on the name provided"""
    similar_names = []
    people_list = people
    for person in people_list:
        if name.lower() in person["name"].lower():
            similar_names.append(person)
    return similar_names

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
