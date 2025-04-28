# create_sample_users.py
from users import UserManager

def create_sample_users():
    """Create sample users for testing"""
    user_manager = UserManager()
    
    # Sample users
    sample_users = [
        {
            "username": "student1",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "email": "student1@umbc.edu",
            "student_id": "AB12345",
            "visa_status": "F-1",
            "program": "Computer Science"
        },
        {
            "username": "student2",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "student2@umbc.edu",
            "student_id": "CD67890",
            "visa_status": "J-1",
            "program": "Information Systems"
        },
        {
            "username": "student3",
            "password": "password123",
            "first_name": "Michael",
            "last_name": "Johnson",
            "email": "student3@umbc.edu",
            "student_id": "EF10111",
            "visa_status": "F-1",
            "program": "Mechanical Engineering"
        }
    ]
    
    for user in sample_users:
        success, message = user_manager.create_user(
            username=user["username"],
            password=user["password"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            student_id=user["student_id"],
            visa_status=user["visa_status"],
            program=user["program"]
        )
        print(f"Creating user {user['username']}: {message}")

if __name__ == "__main__":
    create_sample_users()