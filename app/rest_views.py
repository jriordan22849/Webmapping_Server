from . import models
from . import serializers
from rest_framework import permissions
from . import permissions as my_permissions
from wmap2017 import settings

from . import serializers
from serializers import UserOtherSerializer

from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import permissions, authentication, status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, LineString, Point, Polygon
from rest_framework.authtoken.models import Token
# from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator

from django.forms import ValidationError
from . import forms
from models import FriendGroup
from models import UserFriendGroup
from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime







class UsersList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserOtherSerializer

    def get_queryset(self):
        return get_user_model().objects.all().order_by("username")

    def get_serializer_context(self):
        return {"request": self.request}


class UserMe_R(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    def get_object(self):
        return get_user_model().objects.get(email=self.request.user.email)


class UserOther_R(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        if "uid" in self.kwargs and self.kwargs["uid"]:
            users = get_user_model().objects.filter(id=self.kwargs["uid"])
        elif "email" in self.kwargs and self.kwargs["email"]:
            users = get_user_model().objects.filter(email=self.kwargs["email"])
        else:
            users = None
        if not users:
            self.other = None
            raise exceptions.NotFound
        self.other = users[0]
        return self.other

    def get_serializer_class(self):
        if self.request.user == self.other:
            return serializers.UserMeSerializer
        else:
            return serializers.UserOtherSerializer


class UpdatePosition(generics.UpdateAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdatePosition, self).dispatch(*args, **kwargs)

    def get_object(self):
        return get_user_model().objects.get(email=self.request.user.email)

    def perform_update(self, serializer, **kwargs):
        try:
            lat1 = float(self.request.data.get("lat", False))
            lon1 = float(self.request.data.get("lon", False))
            # lat2 = float(self.request.query_params.get("lat", False))
            # lon2 = float(self.request.query_params.get("lon", False))
            if lat1 and lon1:
                point = Point(lon1, lat1)
            # elif lat2 and lon2:
            #     point = Point(lon2, lat2)
            else:
                point = None

            if point:
                # serializer.instance.last_location = point
                serializer.save(last_location = point)
           
            return serializer
        except:
            pass


@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def token_login(request):
    if (not request.GET["username"]) or (not request.GET["password"]):
        return Response({"detail": "Missing username and/or password"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.GET["username"], password=request.GET["password"])
    if user:
        if user.is_active:
            login(request, user)
            try:
                my_token = Token.objects.get(user=user)
                return Response({"token": "{}".format(my_token.key)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": "Could not get token"})
        else:
            return Response({"detail": "Inactive account"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Invalid User Id of Password"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def token_signup(request):
	
	username = request.GET['username']
	first_name = request.GET['first_name']
	last_name = request.GET['last_name']
	email = request.GET['email']
	password = request.GET['password']
	
	print("username: " + username)
	print("first_name: " + first_name)
	print("last_name: " + last_name)
	print("email: " + email)
	print("password: " + password)
	
	try:
		user = get_user_model().objects.get(username=username)
		if user:
			return Response({"detail": "Inactive account"}, status=status.HTTP_400_BAD_REQUEST)
	except get_user_model().DoesNotExist:
		user = get_user_model().objects.create_user(username=username)
		# Set user fields provided
		user.set_password(password)
		user.first_name = first_name
		user.last_name = last_name
		user.email = email
		user.save()
		return Response({"detail": "Missing username and/or password"}, status=status.HTTP_200_OK)
	          
	return Response({"detail": "Missing username and/or password"}, status=status.HTTP_200_OK)
	
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def token_addgroup(request):
	username = request.GET['username']
	group_name = request.GET['group_name']
	
	user = get_user_model().objects.get(username=username)
	
	group = models.FriendGroup()
	group.name = group_name
	group.owner =  user
 	group.save()
	
	
	print("username " + username)
	print("group_name " + group_name)
	return Response({"detail": "Missing username and/or password"}, status=status.HTTP_200_OK)


# Function to deisplay the list of user in memebers
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def listfriends(request):
	username = request.GET['username']
	group_name = request.GET['groupname']
	print(username)
	print(group_name)
	user = get_user_model().objects.get(username=username)
	group = FriendGroup.objects.get(owner = user,name = group_name)
	friendList = list(UserFriendGroup.objects.filter(friend_group = group).values("member_id"))
	
	userList  = []
	for item in friendList:
		print(item["member_id"])
		user = get_user_model().objects.get(id=item["member_id"]).get_username()
		userList.append(user)
		
	print userList
	userList = list(userList)
	nl = [s.encode('utf-8') for s in userList]
	
		
	
	
	return Response({"friendList": nl},status=status.HTTP_200_OK)

#Return the groups owened by a user.
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def token_getGroups(request):
	username = request.GET['username']
	user = get_user_model().objects.get(username=username)
	groups = FriendGroup.objects.filter(owner=user).values('name')
	print(groups)
	return Response({"groups": groups},status=status.HTTP_200_OK)



@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def addfriend(request):
	username = request.GET['username']
	group_name = request.GET['groupname']
	friendToAdd = request.GET['person']
	
	if( (username != "") and (group_name != "") and (friendToAdd != "")):
		print("Usrrname : " + username + " ,Group name : " + group_name + " ,Friend to add : " + friendToAdd)
		
		# Check if user and group exist
		user = get_user_model().objects.get(username=username)	
		group = FriendGroup.objects.get(owner = user,name = group_name)
		person = get_user_model().objects.get(username=friendToAdd)
		
		if user == person:
			return Response({"Failure": "Failure"},status=HTTP_400_BAD_REQUEST)
		if group and user and person:
			print("User,group name and friend to add exist")
			
			# create an instance of the friend 
			mem = models.UserFriendGroup()
			mem.member = person
			mem.friend_group = group
			mem.save()
			
			return Response({"Success": "Success"},status=status.HTTP_200_OK)
		else:
			return Response({"Failure": "Failure"},status=HTTP_400_BAD_REQUEST)
	else:
		return Response({"Failure": "blank"},status=HTTP_400_BAD_REQUEST)
	return Response({"Success": "Success"},status=status.HTTP_200_OK)
	

@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def addeventtomap(request):

	user = request.GET['username']
	event_name = request.GET['event_name']
	event_time = request.GET['event_time']
	lat = request.GET['lat']
	lon = request.GET['lon']
	
	print(user)
	print(event_name)
	print(lat)
	print(lon)
	print(event_time)
	
	owner = get_user_model().objects.get(username=user)
	
	if event_name != "" and lat != "" and lon != "":
	
		event = models.Events()
		event.member = owner
		event.name = event_name
		event.latitude = lat
		event.longitude = lon
		event.time = event_time
		event.numberofpeople = str(1)
		event.save()	
		return Response({"Success": "Event added from server"},status=status.HTTP_200_OK)
	else:
		return Response({"Failure": "Something went wrong"},status=HTTP_400_BAD_REQUEST)
	
	

	
	
class getListOfFriends(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(getListOfFriends, self).dispatch(*args, **kwargs)

    def get_object(self):
	    username = self.request.GET['username']
	    group_name = self.request.GET['groupname']
	    print("Username: " +username+ " Group name: " + group_name)
	    user = get_user_model().objects.get(username=self.request.GET['username'])
	    group = FriendGroup.objects.get(owner = user,name = self.request.GET['groupname'])
	    friendList = UserFriendGroup.objects.filter(friend_group = group)
	    print friendList.member
	    return get_user_model().objects.get(username=self.request.GET['username'])


		
# Get user information
class getUserPosition(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(getUserPosition, self).dispatch(*args, **kwargs)

    def get_object(self):
	    username = self.request.GET['username']
	    print("Search: " + username)
	    return get_user_model().objects.get(username=self.request.GET['username'])

    def perform_update(self, serializer, **kwargs):
		print("Hello")
	

@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt	
def displayevents(request):
	now = datetime.datetime.now()
	earlier = now - datetime.timedelta(hours=24)
	#events = models.Events.objects.all().values("name", "latitude", "longitude", "member", "time")
	events = models.Events.objects.filter(created__range=(earlier,now)).values("name", "latitude", "longitude", "member", "time","created")
	
	jsonData = list(events)
	print(jsonData)
	return Response({"Success": jsonData},status=status.HTTP_200_OK)
	
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt	
def geteventusername(request):
	id = self.request.GET['id']
	user = get_user_model().objects.get(id=id).values("username")
	print username
	return Response({"Success": jsonData},status=status.HTTP_200_OK)

@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt	
def getusernamebyid(request):
	id = request.GET['id']
	user = get_user_model().objects.get(id=id).get_username()
	print user
	return Response({"Success": user},status=status.HTTP_200_OK)
	
@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt	
def eventinformation(request):
	name = request.GET['name']
	lat = request.GET['lat']
	longitude = request.GET['long']
	
	print(name)
	print(lat)
	print(longitude)
	
	events = models.Events.objects.filter(name=name, latitude=lat,longitude=longitude).values("time","numberofpeople","member")

	events = list(events)
	return Response({"Success": events},status=status.HTTP_200_OK)

@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt	
def updatenumberofattending(request):
	name = request.GET['name']
	lat = request.GET['lat']
	longitude = request.GET['long']
	
	print(name)
	print(lat)
	print(longitude)
	
	events = models.Events.objects.filter(name=name, latitude=lat,longitude=longitude)

	for val in events:
		value =  int(val.numberofpeople)
	
	print("Old value :" + str(value))
	value = value + 1
	print("New value :" + str(value))
	
	ev = models.Events.objects.get(name=name, latitude=lat,longitude=longitude)
	ev.numberofpeople = str(value)
	
	ev.save()

		
	return Response({"Success": "events"},status=status.HTTP_200_OK)
	
	


		