from pydantic import BaseModel
from typing import List

class SalesContact(BaseModel):
    email: str
    phone: str

class Company(BaseModel):
    name: str
    linkedin: str
    size: str
    funding: int
    founded: int
    head_office: str
    sales_dept: SalesContact
