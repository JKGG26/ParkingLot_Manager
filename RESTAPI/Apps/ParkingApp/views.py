from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views import View
from django.contrib.auth.models import User, Group
from django.db.models import Count, Sum

from datetime import datetime, timezone, timedelta, date
from .authentication import generate_jwt, jwt_authenticate, jwt_decode
from .utils.http_utils import get_post_params, get_json_body
from .utils.data_utils import utc_to_local, local_to_utc

from .models import BlackListTokenAccess, ParkingLot, User_ParkingLots
from .models import VehicleParkingRegister, VehicleParkingHistorical, ParkingDailyIncomes


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


@csrf_exempt
def Logout_user(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if auth_header:
            prefix, token = auth_header.split(' ')
            user = jwt_authenticate(token)
            # Check if user was authenticated successfully
            if user is None:
                return JsonResponse({'error': 'Access Denied'}, status=401)
            
            payload = jwt_decode(token)
            expired_at = datetime.fromtimestamp(payload["exp"]).astimezone(timezone.utc).isoformat()
            # Add current token to the Blacklist of tokens
            invalid_token = BlackListTokenAccess(
                token = token,
                expired_at = expired_at,
                user_id = user
            )
            invalid_token.save()
            return JsonResponse({'message': f"Succesfull Log Out"})
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})


#################################
### CRUD PARKING LOTS (ADMIN) ###
#################################
# ----------- CREATE ---------- #
@csrf_exempt
def create_parking_lot(request):
    if request.method == 'POST':
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
                params_required = ['name', 'max_num_vehicles', 'price_per_hour']
                params_gotten, msg = get_post_params(request, params_required)
                if msg is not None:
                    return JsonResponse({'error': f"{msg}"}, status=400)
                
                try:
                    # Create the new ParkingLot
                    parking_lot = ParkingLot(
                        name = params_gotten['name'],
                        max_num_vehicles = params_gotten['max_num_vehicles'],
                        price_per_hour = params_gotten['price_per_hour'],
                    )
                    # Save the new parking lot in the database
                    parking_lot.save()
                    return JsonResponse({'id': parking_lot.id}, status=201)
                except:
                    return JsonResponse({'error': 'Item cannot be created'}, status=400)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

# ---------- GET ALL ---------- #
def list_parking_lots(request):
    if request.method == 'GET':
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
            try:
                if 'Admin' in user_groups_names:
                    parking_lots = [parking.get_properties() for parking in ParkingLot.objects.all()]
                    return JsonResponse(parking_lots, safe=False, status=200)
                elif 'Socio' in user_groups_names:
                    # Get User_ParkingLots relation for current 'Socio'
                    user_parking_lots = User_ParkingLots.objects.filter(user_id=user.id)
                    # Get parkingLots
                    parking_lots = [user_parking.parking_id.get_properties() for user_parking in user_parking_lots]
                    return JsonResponse(parking_lots, safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except:
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

# ------------ GET ------------ #
def get_parking_lot(request, id):
    if request.method == 'GET':
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
                try:
                    parking_lot = ParkingLot.objects.get(id=id)
                    return JsonResponse(parking_lot.get_properties(), status=200)
                except:
                    return JsonResponse({'error': 'Item not found'}, status=404)
            elif 'Socio' in user_groups_names:
                # Get parking lots associated to current 'Socio'
                #parking_lots_associated = User_ParkingLots.objects.get(user_id=user.id)
                #parking_lots_ids = [parking_rel.parking_lot_id]
                parking_lot = ParkingLot.objects.get(id=id)
                return JsonResponse(parking_lot.get_properties(), status=200)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

# ----------- DELETE ----------- #
@csrf_exempt
def delete_parking_lot(request, id):
    if request.method == 'DELETE':
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
                try:
                    parking_lot = ParkingLot.objects.get(id=id)
                    parking_lot.delete()
                    return JsonResponse({}, status=204)
                except:
                    return JsonResponse({'error': 'Item not found'}, status=404)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

# ------------ EDIT ----------- #
@csrf_exempt
def edit_parking_lot(request, id):
    if request.method == 'PUT':
        auth_header = request.headers.get('Authorization')
        if auth_header:
            prefix, token = auth_header.split(' ')
            user = jwt_authenticate(token)
            # Check if user was authenticated successfully
            if user is None:
                return JsonResponse({'error': 'Access Denied'}, status=401)
            
            body_dict, msg = get_json_body(request)
            if len(body_dict) == 0:
                if msg is None:
                    return JsonResponse({'error': 'Invalid JSON'}, status=402)
                return JsonResponse({'error': msg}, status=402)
            # Get user groups QuerySet
            user_groups = user.groups.values_list()
            # Get user groups names
            user_groups_names = [group_set[1] for group_set in user_groups]
            if 'Admin' in user_groups_names:
                try:
                    parking_lot = ParkingLot.objects.get(id=id)
                    # Update fields
                    parking_lot.set_fields(body_dict)
                    # Save changes
                    parking_lot.save()
                    return JsonResponse(parking_lot.get_properties(), status=200)
                except:
                    return JsonResponse({'error': 'Item not found'}, status=404)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

##################################
### ASSOCIATE PARKINGS (ADMIN) ###
##################################
# ---- Set Socio to Parking ---- #
@csrf_exempt
def set_socio_parking(request):
    if request.method == 'POST':
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
                params_required = ['username', 'parking_name']
                params_gotten, msg = get_post_params(request, params_required)
                if msg is not None:
                    return JsonResponse({'error': f"{msg}"}, status=400)
                
                try:
                    # Get the ParkingLot to assign to the 'Socio'
                    parking_lot = ParkingLot.objects.get(name=params_gotten['parking_name'])
                    # Get the user to assign to the ParkingLot
                    socio = User.objects.get(username=params_gotten['username'])
                    socio_groups = socio.groups.values_list()
                    # Get user groups names
                    socio_groups_names = [group_set[1] for group_set in socio_groups]
                    if 'Socio' not in socio_groups_names:
                        raise Exception("Username cannot be related to parking lot")
                    # Create new record for relation 'User_ParkingLots'
                    user_parking = User_ParkingLots(
                        user_id = socio,
                        parking_id = parking_lot,
                        relation_id = f"{parking_lot.name}-{socio.username}"
                    )
                    # Save the new parking lot in the database
                    user_parking.save()
                    return JsonResponse({'id': user_parking.id}, status=201)
                except (ParkingLot.DoesNotExist, User.DoesNotExist):
                    return JsonResponse({'error': 'Items do not exist'}, status=400)
                except:
                    return JsonResponse({'error': 'Item cannot be created'}, status=400)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

# ----------- DELETE ----------- #
@csrf_exempt
def delete_user_parking_relation(request, id):
    if request.method == 'DELETE':
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
                try:
                    user_parking = User_ParkingLots.objects.get(id=id)
                    user_parking.delete()
                    return JsonResponse({}, status=204)
                except:
                    return JsonResponse({'error': 'Item not found'}, status=404)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

#################################
#### RECORD VEHICLES (SOCIO) ####
#################################
# ----------- RECORD ---------- #
@csrf_exempt
def register_vehicle_entry(request):
    if request.method == 'POST':
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
            if 'Socio' in user_groups_names:
                params_required = ['vehicle_plate', 'parking_id', 'parking_spot', 'remarks']
                body_dict, msg = get_json_body(request, params_required)
                if len(body_dict) == 0:
                    if msg is None:
                        return JsonResponse({'error': 'Invalid JSON'}, status=402)
                    return JsonResponse({'error': msg}, status=402)
                
                # Check if 'vehicle_plate' achieve the requirements
                if len(body_dict['vehicle_plate']) != 6 or not str(body_dict['vehicle_plate']).isalnum() or 'ñ' in body_dict['vehicle_plate'].lower():
                    return JsonResponse({'error': f"Vehicle plate '{body_dict['vehicle_plate']}' is invalid"}, status=402)
                
                # Check if 'vehicle_plate' is in any parking lot
                try:
                    existing_vehicle = VehicleParkingRegister.objects.get(vehicle_plate=body_dict['vehicle_plate'])
                    return JsonResponse({'message': "Entry cannot be registered, the plate already exists in this or another parking lot"}, status=400)
                except:
                    pass
                
                try:
                    # Get ParkingLot item from parking_id
                    parking_lot = ParkingLot.objects.get(id = body_dict['parking_id'])
                    # Check if parking gotten is associated to current 'Socio'.
                    # If relation does not exist an Exception is raised (Variable not used)
                    user_parking_lots = User_ParkingLots.objects.get(parking_id=parking_lot.id, user_id=user.id)
                    ### Check availability of parking spot in selected parking lot ###
                    # Get parking lot capacity
                    capacity = parking_lot.max_num_vehicles
                    # Get amount of busy parking spots in parking lot
                    busy_capacity = len(VehicleParkingRegister.objects.filter(parking_id=parking_lot.id))
                    if busy_capacity == capacity:
                        return JsonResponse({'message': 'There are not free spots in this parking lot'}, status=400)
                    # Check if the expected parking spot is available
                    try:
                        parking_spot = VehicleParkingRegister.objects.get(parking_id=parking_lot.id, parking_spot=body_dict['parking_spot'])
                        return JsonResponse({'message': f"Spots '{body_dict['parking_spot']}' is not available in this parking lot"}, status=400)
                    except:
                        pass
                    # Create the new ParkingLot
                    vehicle_entry = VehicleParkingRegister(
                        vehicle_plate = body_dict['vehicle_plate'],
                        parking_id = parking_lot,
                        parking_spot = body_dict['parking_spot'],
                        remarks = body_dict['remarks'],
                    )
                    # Save the new parking lot in the database
                    vehicle_entry.save()
                    return JsonResponse({'id': vehicle_entry.id}, status=201)
                except ParkingLot.DoesNotExist:
                    return JsonResponse({'error': 'Parking not found'}, status=404)
                except User_ParkingLots.DoesNotExist:
                    return JsonResponse({'error': f'Access Denied'}, status=404)
                except:
                    return JsonResponse({'error': f'Item cannot be created'}, status=400)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})


# ----------- OUTPUT ---------- #
@csrf_exempt
def register_vehicle_exit(request):
    if request.method == 'POST':
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
            if 'Socio' in user_groups_names:
                params_required = ['vehicle_plate']
                body_dict, msg = get_json_body(request, params_required)
                if len(body_dict) == 0:
                    if msg is None:
                        return JsonResponse({'error': 'Invalid JSON'}, status=402)
                    return JsonResponse({'error': msg}, status=402)
                
                # Check if 'vehicle_plate' achieve the requirements
                if len(body_dict['vehicle_plate']) != 6 or not str(body_dict['vehicle_plate']).isalnum() or 'ñ' in body_dict['vehicle_plate'].lower():
                    return JsonResponse({'error': f"Vehicle plate '{body_dict['vehicle_plate']}' is invalid"}, status=402)
                
                try:
                    # Check if 'vehicle_plate' is in any parking lot and get object
                    vehicle_entry = VehicleParkingRegister.objects.get(vehicle_plate=body_dict['vehicle_plate'])
                    # Get ParkingLot item from parking_id
                    parking_lot = vehicle_entry.parking_id
                    # Check if parking gotten is associated to current 'Socio'.
                    # If relation does not exist an Exception is raised (Variable not used)
                    user_parking_lots = User_ParkingLots.objects.get(parking_id=parking_lot.id, user_id=user.id)
                    print(user_parking_lots)
                    exit_time = datetime.now(timezone.utc)
                    delta_time = exit_time - vehicle_entry.entry_time#.replace(tzinfo=None)
                    hours = 1 + int(delta_time.total_seconds() / 3600)
                    # Create the new ParkingLot
                    vehicle_historical = VehicleParkingHistorical(
                        vehicle_plate = vehicle_entry.vehicle_plate,
                        entry_time = vehicle_entry.entry_time,
                        parking_id = vehicle_entry.parking_id,
                        parking_spot = vehicle_entry.parking_spot,
                        remarks = vehicle_entry.remarks,
                        exit_time = exit_time,
                        hours = hours,
                        income = hours * parking_lot.price_per_hour
                    )
                    # Save the new vehicle exit in historical in the database
                    vehicle_historical.save()
                    # Delete the vehicle register from 'VehicleParkingRegister'
                    vehicle_entry.delete()
                    return JsonResponse({'message': 'Registered exit'}, status=200)
                except VehicleParkingRegister.DoesNotExist:
                    return JsonResponse({'message': "Exit cannot be registered, the plate does not exist in any parking lot"}, status=404)
                except ParkingLot.DoesNotExist:
                    return JsonResponse({'error': 'Parking not found'}, status=404)
                except User_ParkingLots.DoesNotExist:
                    return JsonResponse({'error': f'Access Denied'}, status=404)
                except Exception as exc:
                    print(exc)
                    return JsonResponse({'error': f'Item cannot be registered'}, status=400)
            else:
                return JsonResponse({'error': 'Permission Denied'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})


# ---------- GET ALL ---------- #
def list_vehicles_entries(request):
    if request.method == 'GET':
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
            try:
                # Define a lambda function to modify inner datetime field
                lbd_func_utc_local = lambda x, field: {**x, field:utc_to_local(x[field])}

                if 'Admin' in user_groups_names:
                    vehicles_entries = [vehicle_entry.get_properties() for vehicle_entry in VehicleParkingRegister.objects.all()]
                    # Apply lambda function to transform every  'entry_time' value to local timezone
                    vehicles_entries = [lbd_func_utc_local(ve, 'entry_time') for ve in vehicles_entries]
                    return JsonResponse(vehicles_entries, safe=False, status=200)
                elif 'Socio' in user_groups_names:
                    # Get User_ParkingLots relation for current 'Socio'
                    parking_lots_ids = [user_parking.parking_id.id for user_parking in User_ParkingLots.objects.filter(user_id=user.id)]
                    # Get parkingLots
                    vehicles_entries = []
                    for parking_id in parking_lots_ids:
                        vehicles_entries_parking = [vehicle_entry.get_properties() for vehicle_entry in VehicleParkingRegister.objects.filter(parking_id = parking_id)]
                        # Apply lambda function to transform every  'entry_time' value to local timezone
                        vehicles_entries.extend([lbd_func_utc_local(ve, 'entry_time') for ve in vehicles_entries_parking])
                    return JsonResponse(vehicles_entries, safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except:
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

# ------------ GET ------------ #
def get_vehicles_entries(request, id):
    if request.method == 'GET':
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
            try:
                # Define a lambda function to modify inner datetime field
                lbd_func_utc_local = lambda x, field: {**x, field:utc_to_local(x[field])}
                    
                if 'Admin' in user_groups_names:
                    # Check if parking_id to get data exists in DB (Only for ADMIN)
                    parking_lot = ParkingLot.objects.get(id=id)
                    # Get all records of vehicles entries for parking_id
                    vehicles_entries = [vehicle_entry.get_properties() for vehicle_entry in VehicleParkingRegister.objects.filter(parking_id=id)]
                    vehicles_entries = [lbd_func_utc_local(ve, 'entry_time') for ve in vehicles_entries]
                    return JsonResponse(vehicles_entries, safe=False, status=200)
                elif 'Socio' in user_groups_names:
                    # Check if current 'Socio' has assigned the parking lot to get data
                    user_parking_lot = User_ParkingLots.objects.get(parking_id=id, user_id=user.id)
                    # Get all records of vehicles entries for parking_id
                    vehicles_entries = [vehicle_entry.get_properties() for vehicle_entry in VehicleParkingRegister.objects.filter(parking_id=id)]
                    vehicles_entries = [lbd_func_utc_local(ve, 'entry_time') for ve in vehicles_entries]
                    return JsonResponse(vehicles_entries, safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except ParkingLot.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
            except User_ParkingLots.DoesNotExist:
                return JsonResponse({'error': 'Access Denied'}, status=401)
            except:
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
    

##################################
########### INDICATORS ###########
##################################
# -- Top all vehicles entries -- #
def top_vehicles_entries(request, top):
    if request.method == 'GET':
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
            try:
                if 'Admin' in user_groups_names:
                    # get counts per vehicle_plate from VehicleParkingHistorical table
                    """ SELECT vehicle_plate, COUNT(*) AS num_entries
                        FROM public."ParkingApp_vehicleparkinghistorical"
                        GROUP BY vehicle_plate
                        ORDER BY num_entries DESC, vehicle_plate;
                    """
                    vehicle_entry_counts = VehicleParkingHistorical.objects.values('vehicle_plate').annotate(number_registers=Count('id')).order_by('-number_registers', 'vehicle_plate')
                    return JsonResponse(list(vehicle_entry_counts)[:top], safe=False, status=200)
                elif 'Socio' in user_groups_names:
                    # Get User_ParkingLots relation for current 'Socio'
                    parking_lots_ids = [user_parking.parking_id.id for user_parking in User_ParkingLots.objects.filter(user_id=user.id)]
                    # Get counts per vehicle_plate from VehicleParkingHistorical table only for the associated parking lots
                    """ SELECT vehicle_plate, COUNT(*) AS num_entries
                        FROM (
                            SELECT * FROM public."ParkingApp_vehicleparkinghistorical"
                            WHERE parking_id IN (id1, id2, ... idn)
                        )
                        GROUP BY vehicle_plate
                        ORDER BY num_entries DESC, vehicle_plate;
                    """
                    vehicle_entry_counts = list(VehicleParkingHistorical.objects.filter(parking_id__in = parking_lots_ids).values('vehicle_plate').annotate(number_registers=Count('id')).order_by('-number_registers', 'vehicle_plate'))
                    return JsonResponse(vehicle_entry_counts[:top], safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except:
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})


# -- Top all vehicles entries -- #
def top_vehicles_entries_parking(request, top, id):
    if request.method == 'GET':
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
            try:
                if 'Admin' in user_groups_names:
                    # get counts per vehicle_plate from VehicleParkingHistorical table
                    """ SELECT vehicle_plate, COUNT(*) AS num_entries
                        FROM public."ParkingApp_vehicleparkinghistorical"
                        WHERE parking_id = id
                        GROUP BY vehicle_plate
                        ORDER BY num_entries DESC, vehicle_plate;
                    """
                    # Check if parking lot exists (Only for ADMIN)
                    parking_lot = ParkingLot.objects.get(id=id)
                    vehicle_entry_counts = VehicleParkingHistorical.objects.filter(parking_id = id).values('vehicle_plate').annotate(number_registers=Count('id')).order_by('-number_registers', 'vehicle_plate')
                    return JsonResponse(list(vehicle_entry_counts)[:top], safe=False, status=200)
                elif 'Socio' in user_groups_names:
                    # Check if current 'Socio' user has access to specified parking lot
                    user_parking = User_ParkingLots.objects.get(parking_id=id, user_id=user.id)
                    # Get counts per vehicle_plate from VehicleParkingHistorical table only for the associated parking lots
                    vehicle_entry_counts = VehicleParkingHistorical.objects.filter(parking_id = id).values('vehicle_plate').annotate(number_registers=Count('id')).order_by('-number_registers', 'vehicle_plate')
                    return JsonResponse(list(vehicle_entry_counts)[:top], safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except ParkingLot.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
            except User_ParkingLots.DoesNotExist:
                return JsonResponse({'error': 'Access Denied'}, status=401)
            except:
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})


# ---------- FIRST TIME ---------- #
def first_time_vehicles_parking(request, id):
    if request.method == 'GET':
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
            try:
                if 'Admin' in user_groups_names:
                    # Check if parking lot exists
                    parking_lot = ParkingLot.objects.get(id=id)
                    # Get registered vehicle_plates
                    registered_vehicles_plates = VehicleParkingHistorical.objects.filter(parking_id=id).values('vehicle_plate').distinct()
                    # Get first time vehicle_plates currently in the parking
                    vehicles_entries = VehicleParkingRegister.objects.filter(parking_id=id).exclude(vehicle_plate__in = registered_vehicles_plates).values('vehicle_plate', 'entry_time')
                    return JsonResponse(list(vehicles_entries), safe=False, status=200)
                elif 'Socio' in user_groups_names:
                    # Get User_ParkingLots relation for current 'Socio'
                    user_parking = User_ParkingLots.objects.get(parking_id=id, user_id=user.id)
                    # Get registered vehicle_plates
                    registered_vehicles_plates = VehicleParkingHistorical.objects.filter(parking_id=id).values('vehicle_plate').distinct()
                    # Get first time vehicle_plates currently in the parking
                    vehicles_entries = VehicleParkingRegister.objects.filter(parking_id=id).exclude(vehicle_plate__in = registered_vehicles_plates).values('vehicle_plate', 'entry_time')
                    return JsonResponse(list(vehicles_entries), safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except ParkingLot.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
            except User_ParkingLots.DoesNotExist:
                return JsonResponse({'error': 'Access Denied'}, status=401)
            except:
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})


# ------ INCOMES PARKING LOT ------ #
def incomes_last_days_parking(request, days, id):
    if request.method == 'GET':
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
            try:
                if 'Socio' in user_groups_names:
                    # Get User_ParkingLots relation for current 'Socio'
                    user_parking = User_ParkingLots.objects.get(parking_id=id, user_id=user.id)
                    # Get current datetime
                    current_date = date.today()
                    current_datetime = datetime(current_date.year, current_date.month, current_date.day,0,0,0,0)
                    # Get the start datetime like today - num_days to get data
                    start_date = local_to_utc(current_datetime) - timedelta(days=days)
                    # Get the end datetime like today to the end of day
                    end_date = local_to_utc(current_datetime + timedelta(days=1))
                    # Get registered vehicle_plates
                    registered_incomes_date = VehicleParkingHistorical.objects.filter(
                        parking_id=id, exit_time__gte = start_date, exit_time__lt = end_date
                        ).aggregate(total_incomes=Sum('income'))
                    # Set the range of date of gotten data
                    registered_incomes_date['start_date'] = start_date.isoformat()[:10]
                    registered_incomes_date['end_date'] = end_date.isoformat()[:10]
                    # Get first time vehicle_plates currently in the parking
                    return JsonResponse(registered_incomes_date, safe=False, status=200)
                else:
                    return JsonResponse({'error': 'Permission Denied'}, status=401)
            except ParkingLot.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
            except User_ParkingLots.DoesNotExist:
                return JsonResponse({'error': 'Access Denied'}, status=401)
            except Exception as exc:
                print(exc)
                return JsonResponse({'error': 'Data not found'}, status=404)
        else:
            return JsonResponse({'error': 'Authorization header required'}, status=401)
    else:
        return JsonResponse({'error': 'Method not supported'})
