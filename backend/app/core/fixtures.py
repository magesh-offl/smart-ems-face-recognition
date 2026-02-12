"""
Data fixtures for database seeding.

This module contains static data definitions that are used
to seed the database during initial setup or testing.

Following the MVC + Layered architecture, fixtures are
separated from the seeding logic (service layer).
"""
from typing import List, Dict, Any


# =============================================
# Course Fixtures (CRS0001 - CRS0010)
# =============================================

COURSES: List[Dict[str, Any]] = [
    {
        "course_id": "CRS0001",
        "name": "Class 10",
        "section": "A",
        "description": "10th Grade Section A"
    },
    {
        "course_id": "CRS0002",
        "name": "Class 10",
        "section": "B",
        "description": "10th Grade Section B"
    },
    {
        "course_id": "CRS0003",
        "name": "Class 11",
        "section": "A",
        "description": "11th Grade Section A"
    },
    {
        "course_id": "CRS0004",
        "name": "Class 11",
        "section": "B",
        "description": "11th Grade Section B"
    },
    {
        "course_id": "CRS0005",
        "name": "Class 12",
        "section": "A",
        "description": "12th Grade Section A"
    },
    {
        "course_id": "CRS0006",
        "name": "Class 12",
        "section": "B",
        "description": "12th Grade Section B"
    },
    {
        "course_id": "CRS0007",
        "name": "B.Tech CSE",
        "section": "1st Year",
        "description": "Computer Science Engineering Year 1"
    },
    {
        "course_id": "CRS0008",
        "name": "B.Tech CSE",
        "section": "2nd Year",
        "description": "Computer Science Engineering Year 2"
    },
    {
        "course_id": "CRS0009",
        "name": "B.Tech CSE",
        "section": "3rd Year",
        "description": "Computer Science Engineering Year 3"
    },
    {
        "course_id": "CRS0010",
        "name": "B.Tech CSE",
        "section": "4th Year",
        "description": "Computer Science Engineering Year 4"
    },
]


# =============================================
# Add additional fixtures below as needed
# =============================================

# Example: Default roles (if not handled by auth service)
# ROLES: List[Dict[str, Any]] = [
#     {"role_id": "ROL0001", "name": "super_admin", "permissions": ["*"]},
#     {"role_id": "ROL0002", "name": "admin", "permissions": [...]},
# ]
