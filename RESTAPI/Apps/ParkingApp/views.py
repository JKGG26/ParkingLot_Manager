from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views import View
from django.contrib.auth.models import User, Group

from .security.authentication import generate_jwt, jwt_authenticate
from .utils.http_utils import get_post_params


@csrf_exempt
def obtain_jwt_token(request):
    if request.method == 'POST':
        params_required = ['username', 'password']
        params_gotten, msg = get_post_params(request, params_required)
        if msg is not None:
            return JsonResponse({'error': f"{msg}"}, status=400)
            
        user = authenticate(username=params_gotten['username'], password=params_gotten['password'])
        if user is not None:
            token = generate_jwt(user)
            return JsonResponse({'token': token})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)
    

@csrf_exempt
def RegisterSocio(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    auth_header = request.headers.get('Authorization')
    if auth_header:
        prefix, token = auth_header.split(' ')
        user = jwt_authenticate(token)
        # Check if user was authenticated successfully
        if user is None:
            return JsonResponse({'error': 'Access Denied'}, status=401)
        # Get user groups QuerySet
        user_groups = user.groups.values_list()
        # Get user groups names
        user_groups_names = [group_set[1] for group_set in user_groups]
        if 'Admin' in user_groups_names:
            # Get credentials for the new 'Socio' to add
            params_required = ['username', 'password']
            params_gotten, msg = get_post_params(request, params_required)
            print(params_gotten, msg)
            if msg is not None:
                return JsonResponse({'error': f"{msg}"}, status=400)
            try:
                # Create new user
                new_user = User.objects.create_user(
                    username=params_gotten['username'],
                    password=params_gotten['password'],
                    email=params_gotten['username'],
                )
                new_user.save()
                # Add new user to group (Role) 'Socio'
                group_socio = Group.objects.get(name='Socio')
                group_socio.user_set.add(new_user)
                return JsonResponse({'message': f'New Socio user, {new_user.username} was created!'}, status=201)
            except:
                return JsonResponse({'error': f"User '{new_user}' could not be created"}, status=400)
        else:
            return JsonResponse({'error': 'Permission Denied'}, status=401)
    else:
        return JsonResponse({'error': 'Authorization header required'}, status=401)
    

class ProtectedView(View):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            prefix, token = auth_header.split(' ')
            user = jwt_authenticate(token)
            # Check if user was authenticated successfully
            if user is not None:
                return JsonResponse({'message': f'Hello, {user.username}!'})
            else:
                return JsonResponse({'error': 'Access Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
        

class AdminOnlyView(View):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            prefix, token = auth_header.split(' ')
            user = jwt_authenticate(token)
            # Check if user was authenticated successfully
            if user is None:
                return JsonResponse({'error': 'Access Denied'}, status=403)
            # Get user groups QuerySet
            user_groups = user.groups.values_list()
            # Get user groups names
            user_groups_names = [group_set[1] for group_set in user_groups]
            print(user_groups_names)
            if 'Admin' in user_groups_names:
                return JsonResponse({'message': f'Hello, Admin {user.username}!'})
            else:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)


class SocioOnlyView(View):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            prefix, token = auth_header.split(' ')
            user = jwt_authenticate(token)
            # Check if user was authenticated successfully
            if user is None:
                return JsonResponse({'error': 'Access denied'}, status=403)
            # Get user groups QuerySet
            user_groups = user.groups.values_list()
            # Get user groups names
            user_groups_names = [group_set[1] for group_set in user_groups]
            print(user_groups_names)
            if user is not None and 'Socio' in user_groups_names:
                return JsonResponse({'message': f'Hello, Socio {user.username}!'})
            else:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)