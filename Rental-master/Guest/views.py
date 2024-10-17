from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
# from .forms import SignUpForm
from django.template import loader
from user.models import *
from datetime import *
import re
import os
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseBadRequest



def index(request):
    template = loader.get_template('index.html')
    context = {}

    room = Room.objects.all()
    if bool(room):
        n = len(room)
        nslide = n // 3 + (n % 3 > 0)
        rooms = [room, range(1, nslide), n]
        context.update({'room': rooms})
    rental = Rentals.objects.all()
    if bool(rental):
        n = len(rental)
        nslide = n // 3 + (n % 3 > 0)
        rentals = [rental, range(1, nslide), n]
        context.update({'rental': rentals})
    return HttpResponse(template.render(context, request))


def home(request):
    template = loader.get_template('home.html')
    context = {}
    context.update({'result': ''})
    context.update({'msg': 'Search your query'})
    return HttpResponse(template.render(context, request))


def search(request):
    template = loader.get_template('home.html')
    context = {}
    if request.method == 'GET':
        typ = request.GET['type']
        q = request.GET['q']
        context.update({'type': typ})
        context.update({'q':q})
        results={}
        if typ == 'Rentals' and (bool(Rentals.objects.filter(location=q)) or bool(Room.objects.filter(city=q))):
            results = Rentals.objects.filter(location=q)
            results = results | Rentals.objects.filter(city=q)
        elif typ == 'Apartment'  and (bool(Room.objects.filter(address=q)) or bool(Rentals.objects.filter(city=q))):
            results = Room.objects.filter(address=q)
            results = results | Room.objects.filter(city=q)
        
        if bool(results)== False:
            print("messages")
            messages.success(request, "No matching results for your query..")

        result = [results, len(results)]
        context.update({'result': result})

    return HttpResponse(template.render(context, request))


def about(request):
    template = loader.get_template('about.html')
    context = {}

    room = Room.objects.all()
    if bool(room):
        context.update({'room': room})
    rental = Rentals.objects.all()
    if bool(rental):
        context.update({'rental': rental})
    return HttpResponse(template.render(context, request))


def descr(request):
    template = loader.get_template('desc.html')
    context = {}
    if request.method == 'GET':
        id = request.GET.get('id')
        try:
            room = Room.objects.get(room_id=id)
            context.update({'val': room})
            context.update({'type': 'Apartment'})
            user = User.objects.get(email=room.user_email)
        except Room.DoesNotExist:
            try:
                rental = Rentals.objects.get(rent_id=id)
                context.update({'val': rental})
                context.update({'type': 'Rentals'})
                user = User.objects.get(email=rental.user_email)
            except Rentals.DoesNotExist:
                return HttpResponseBadRequest("Rental not found")
            except User.DoesNotExist:
                return HttpResponseBadRequest("User not found")
            
    context.update({'user': user})
    return HttpResponse(template.render(context, request))


# def loginpage(request):
#     return render(request, 'login.html', {'msg': ''})


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {'msg': ''})

    name = request.POST['name']
    email = request.POST['email']
    location = request.POST['location']
    city = request.POST['city']
    state = request.POST['state']
    phone = request.POST['phone']
    pas = request.POST['pass']
    cpas = request.POST['cpass']
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        pass
    else:
        template = loader.get_template('register.html')
        context = {'msg': 'invalid email'}
        return HttpResponse(template.render(context, request))

    if len(str(phone)) != 10:
        template = loader.get_template('register.html')
        context = {'msg': 'invalid phone number'}
        return HttpResponse(template.render(context, request))

    if pas != cpas:
        template = loader.get_template('register.html')
        context = {'msg': 'password did not matched'}
        return HttpResponse(template.render(context, request))
    already = User.objects.filter(email=email)
    if bool(already):
        template = loader.get_template('register.html')
        context = {'msg': 'email already registered'}
        return HttpResponse(template.render(context, request))
    
    user = User.objects.create_user(
        name=name,
        email=email,
        location=location,
        city=city,
        state=state,
        number=phone,
        password=pas,
        )
    user.save()
    login(request, user)
    return redirect("/login/")

@login_required(login_url='/login')
def profile(request):
    room = Room.objects.filter(user_email=request.user)
    rental = Rentals.objects.filter(user_email=request.user)
    roomcnt = room.count()
    rentalcnt = rental.count()
    rooms = []
    rentals = []
    if bool(room):
        n = len(room)
        nslide = n // 3 + (n % 3 > 0)
        rooms = [room, range(1, nslide), n]
    if bool(rental):
        n = len(rental)
        nslide = n // 3 + (n % 3 > 0)
        rentals = [rental, range(1, nslide), n]
        
    context = {
        'user': request.user,
        'roomno': roomcnt,
        'rentalno': rentalcnt
    }
    context.update({'room': rooms})
    context.update({'rental': rentals})    
    return render(request, 'profile.html', context=context)


@login_required(login_url='/login')
def post(request):
    if request.method == "GET":
        context = {'user': request.user}
        return render(request, 'post.html', context)
    elif request.method == "POST":
        try:
            address = request.POST['address'].lower()  
            city = request.POST['city'].lower()
            state = request.POST['state'].lower()
            dimension = request.POST['dimension'] 
            cost = int(request.POST['cost'])  
            hall = request.POST['hall'].lower()
            kitchen = request.POST['kitchen'].lower()
            balcony = request.POST['balcony'].lower()  
            bedrooms = int(request.POST['bedroom'])  
            ac = request.POST['AC'].lower()
            desc = request.POST['desc'].upper()
            img = request.FILES['img']  
            user_obj = User.objects.get(email=request.user.email)

            room = Room.objects.create(
                user_email=user_obj,
                address=address,  
                city=city,
                state=state,
                dimension=dimension,  
                cost=cost,
                hall=hall,
                kitchen=kitchen,
                balcony=balcony,  
                bedrooms=bedrooms,
                AC=ac,
                desc=desc,  
                img=img,
            )
            messages.success(request, 'Accommodation Listing Submitted Successfully!')
            return render(request, 'post.html')
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'An error occurred while submitting the accommodation listing.')
            return HttpResponse(status=500)


@login_required(login_url='/login')
def post_rental(request):
    if request.method == "GET":
        context = {'user': request.user}
        return render(request, 'post_rental.html', context)
    else:
        try:
            item_name = request.POST['item_name']
            rent_sale = request.POST['rent_sale']
            location = request.POST['location'].lower()
            city = request.POST['city'].lower()
            state = request.POST['state'].lower()
            cost = request.POST['cost']
            year = request.POST['year']
            condition = request.POST['condition'].upper()  
            desc = request.POST['desc']
            img = request.FILES['img']

            cost = float(cost)  
            year = int(year)   
            user_obj = User.objects.filter(email=request.user.email)[0]

            rental = Rentals.objects.create(
                user_email=user_obj,
                item_name=item_name,
                rent_sale=rent_sale,
                location=location,
                city=city,
                state=state,
                cost=cost,
                year=year,
                condition=condition,
                desc=desc,
                img=img,
            )
            messages.success(request, 'Rental & Sales Listing Submitted Successfully!')
            return render(request, 'post_rental.html')
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

def deleter(request):
    if request.method == 'GET':
        id = request.GET['id']
        instance = Room.objects.get(room_id=id)
        instance.delete()
        messages.success(request, 'Appartment Listing Deleted Successfully!')
    return redirect('/profile')

def deleteh(request):
    if request.method == 'GET':
        id = request.GET['id']
        instance = Rentals.objects.get(rent_id=id)
        instance.delete()
        messages.success(request, 'Rental & Sales Listing Deleted Successfully!')
    return redirect('/profile')


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, email=email, password=password)

    if user is not None:
        login(request, user)
        return redirect("/index")
    else:
        template = loader.get_template('login.html')
        context = {
            'msg': 'Email and password, you entered, did not matched.'
        }
        return HttpResponse(template.render(context, request))
    
def logout_view(request):
    logout(request)
    return redirect('/index')  # Redirect to the homepage

