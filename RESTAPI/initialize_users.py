import os
import django
# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RESTAPI.settings')
# Initialize Django
django.setup()

# Start code for project
from django.contrib.auth.models import User, Group


def create_roles(roles: list):
    for role in roles:
        group, created = Group.objects.get_or_create(name=role)
        if created:
            print(f"Group '{role}' created successfully.")
        else:
            print(f"Group '{role}' already exists.")


def create_main_user(env_user_variables: list, role: str):
    # Get user and password from env variables
    username = os.environ[env_user_variables[0]]
    password = os.environ[env_user_variables[1]]
    try:
        # Create User
        user = User.objects.create_user(username=username, password=password)
        user.email = username
        user.save()
        print(f"User '{user.username}' created successfully.")
        # Assign main user to admin role (group)
        group = Group.objects.get(name=role)
        group.user_set.add(user)
        print(f"User '{user.username}' added to group '{role}'.")
    except Exception as exc:
        #print(exc)
        print("\n\nUser could not be created")


def initialize_users():
    roles = ["Admin", "Socio"]
    env_user_variables = ["ADMIN_USER", "ADMIN_PWD"]
    # Create groups if not exist
    create_roles(roles)
    # Create main user if not exists
    create_main_user(env_user_variables, roles[0])


if __name__ == '__main__':
    initialize_users()
