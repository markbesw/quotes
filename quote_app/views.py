from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt, re
from .models import *

# Create your views here.

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method=="POST":
        errors = User.objects.validate(request.POST)
        if errors:
            for error in errors:
                messages.error(request, errors[error])
            return redirect('/')

        # password encrypt
        user_pw = request.POST['pw']
        hash_pw = bcrypt.hashpw(user_pw.encode(), bcrypt.gensalt()).decode()

        # create the new user
        new_user = User.objects.create(first_name=request.POST['f_n'], last_name=request.POST['l_n'], email=request.POST['email'], password=hash_pw)
        print(f"first_name:{request.POST['f_n']}, last_name:{request.POST['l_n']}, email:{request.POST['email']}, password:{request.POST['pw']}, (hash: {hash_pw}).")

        # store info in session
        request.session['user_id'] = new_user.id
        request.session['user_name'] = f"{new_user.first_name} {new_user.last_name}"
        request.session['acct_error'] = ''   # first time in, make sure session error var is empty

        return redirect('/quotes')
    return redirect('/')

def login(request):
    if request.method == 'POST':
        # see if email is in the DB
        logged_user = User.objects.filter(email=request.POST['email'])
        if logged_user:
            logged_user = logged_user[0]    # strip the curlies 
            # compare the passwords
            if bcrypt.checkpw(request.POST['pw'].encode(), logged_user.password.encode()):
                request.session['user_id'] = logged_user.id
                request.session['user_name'] = f"{logged_user.first_name} {logged_user.last_name}"
                request.session['acct_error'] = ''   # first time in, make sure session error var is empty
                return redirect('/quotes')
            else:
                messages.error(request, "Incorrect password!")
                return redirect('/')
        else:
            messages.error(request, f"Sorry, I couldn't locate {request.POST['email']} in our database. Please try again.")
            return redirect('/')
    else:
        return redirect('/')

def logout(request):
    request.session.clear()
    return redirect('/')
    
def quotes(request):
    if 'user_id' not in request.session:
        return redirect("/")
    
    # get all the quotes, pass to board thru context
    context = {
        'all_quotes': Quote.objects.all().order_by('-created_at')
    }
    return render(request, "quotes.html", context)

def create_quote(request):
    if request.method == 'POST':
        # validate
        errors = Quote.objects.validate(request.POST)
        if errors:
            print("validation error")
            for error in errors:
                messages.error(request, errors[error])
            return redirect('/quotes')

        # create quote in DB
        content = request.POST['content']
        quoter = request.POST['quoter']
        u = User.objects.get(id=request.session['user_id'])
        print(f"con: {content}, qtr: {quoter}, poster: {u.email}")
        Quote.objects.create(content=content, quoter=quoter, poster=u, likes=0)
        return redirect('/quotes')
    else:
        return redirect('/')

def user(request, user_id):
    # render user's profile page, listing all of user's posted quotes
    u = User.objects.get(id=user_id)
    q = u.quotes
    context = {
        'user': u,
        'quotes': q
    }
    print(f"In user, user last name = {u.last_name}")
    return render(request, "profile.html", context)

def myaccount(request, user_id):
    # get the user object, pass it thru context to myaccount page
    u = User.objects.get(id=user_id)
    context = {
        'user': u
    }
    print(f"In myaccount, user last name = {u.last_name}")
    return render(request, "myaccount.html", context)

def delete_post(request, quote_id):
    q = Quote.objects.get(id=quote_id)
    q.delete()
    return redirect('/quotes')

def update_account(request):
    if request.method == 'POST':
        # get user object, retrieve form fields.
        uid = request.session['user_id']
        u = User.objects.get(id=uid)
        u_fn = request.POST['f_n']
        u_ln = request.POST['l_n']
        u_em = request.POST['email']

        # form up redirect path with user_id
        redir_path = "/myaccount/" + str(uid)
        # redir_path = "/acct_error"  (v1)

        # Validate fields
        errors = {}         # to hold error strings, if needed
        if len(u_fn) < 2:
            # (v1) request.session['acct_error'] = "First name must be 2 or more characters."
            errors['fn_err'] = "First name must be 2 or more characters."
        if len(u_ln) < 2:
            errors['ln_err'] = "Last name must be 2 or more characters."
        # check that email is not in use (special case: current user email OK)
        if u.email == u_em:
            # current user's email address is OK
            pass
        else:
            email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
            if len(u_em) == 0:
                errors['no_em_err'] = "You need to supply an email address."
            if not email_check.match(u_em):
                errors['bad_em_err'] = "Invalid email address"
            # check to see if email is already in use
            qs = User.objects.filter(email=u_em)
            if qs:
                errors['used_em_err'] = f"Email address {u_em} is already in use."
        if errors:
            for err in errors:
                messages.error(request, errors[err])
            return redirect(redir_path)

        # update user object and user name in session
        u.first_name = u_fn
        u.last_name = u_ln
        u.email = u_em
        u.save()
        request.session['user_name'] = f"{u_fn} {u_ln}"
        return redirect('/quotes')
    
    else:
        # not a post request, redirect to /
        return redirect('/')

def acct_error(request):
    return render(request, 'acct_error.html')