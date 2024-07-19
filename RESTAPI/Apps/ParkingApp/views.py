from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views import View
from .security.authentication import generate_jwt, jwt_authenticate


@csrf_exempt
def obtain_jwt_token(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token = generate_jwt(user)
            return JsonResponse({'token': token})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)


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
                return JsonResponse({'error': 'Invalid token'}, status=401)
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
                return JsonResponse({'error': 'Permission denied or invalid token'}, status=403)
            # Get user groups QuerySet
            user_groups = user.groups.values_list()
            # Get user groups names
            user_groups_names = [group_set[1] for group_set in user_groups]
            print(user_groups_names)
            if 'Admin' in user_groups_names:
                return JsonResponse({'message': f'Hello, Admin {user.username}!'})
            else:
                return JsonResponse({'error': 'Permission denied or invalid token'}, status=403)
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
                return JsonResponse({'error': 'Permission denied or invalid token'}, status=403)
            # Get user groups QuerySet
            user_groups = user.groups.values_list()
            # Get user groups names
            user_groups_names = [group_set[1] for group_set in user_groups]
            print(user_groups_names)
            if user is not None and 'Socio' in user_groups_names:
                return JsonResponse({'message': f'Hello, Socio {user.username}!'})
            else:
                return JsonResponse({'error': 'Permission denied or invalid token'}, status=403)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)