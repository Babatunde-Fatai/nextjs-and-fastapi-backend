from langchain_core.tools import tool
import random
from ..data.data import dummy_data


# my custom tools
@tool("lower_case", return_direct=False)
def to_lower_case(input:str) -> str:
  """Returns the input as all lower case."""
  return input.lower()

@tool("random_number", return_direct=False)
def random_number_maker(input:str) -> str:
    """Returns a random number between 0-100. input the word 'random'"""
    return random.randint(0, 100)


people = [
    {"name": "John Doe", "age": 35, "city": "New York"},
    {"name": "Jane Smith", "age": 28, "city": "Los Angeles"},
    {"name": "Michael Johnson", "age": 42, "city": "Chicago"},
    {"name": "Emily Davis", "age": 31, "city": "San Francisco"},
    {"name": "David Wilson", "age": 27, "city": "Boston"},
    {"name": "Sophia Thompson", "age": 39, "city": "Seattle"},
    {"name": "Daniel Anderson", "age": 25, "city": "Miami"},
    {"name": "Babatunde Fatai", "age": 33, "city": "Dallas"},
    {"name": "William Jackson", "age": 29, "city": "Houston"},
    {"name": "Emma Garcia", "age": 37, "city": "Philadelphia"}
]


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

  if requisition_number in dummy_data:
    return dummy_data[requisition_number]
  else:
    return 'Details of this requisition was not found'