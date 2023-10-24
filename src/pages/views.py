from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import transaction
from .models import Account
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import logging, time
log = logging.getLogger("django")

@transaction.atomic
def transfer(sender, receiver, amount):
	if amount <= 0: return 0
	if sender == receiver: return 0

	acc1 = Account.objects.get(user=sender)
	acc2 = Account.objects.get(user=receiver)

	if acc1.balance < amount:
		return 0

	acc1.balance -= amount
	acc2.balance += amount

	acc1.save()
	acc2.save()

	return 1


@login_required
def transferView(request, user):
	#2.accessctrl.better
	# if request.user.username != user:
	# 	return redirect("/")

	if request.method == 'POST':
		sender = request.user
		to = User.objects.get(username=request.POST.get('to'))
		amount = int(request.POST.get('amount'))

		r = transfer(sender, to, amount)

		#5.logging.better
		# if r == 1:
		# 	log.info(f"Transfer request for \"{get_client_ip(request)}\" completed, (sender: {sender.username}, to: {to.username}, amount: {amount})")
		# else:
		# 	log.info(f"Transfer request for \"{get_client_ip(request)}\" failed, (sender: {sender.username}, to: {to.username}, amount: {amount})")
	
	return redirect('/user/' + user)



@login_required
def homePageView(request, user):
	#2.accessctrl.better
	#if request.user.username != user:
	#	return redirect("/user/"+request.user.username)

	curUser = User.objects.get(username=user)
	accounts = Account.objects.exclude(user=curUser)

	return render(request, 'pages/index.html', {"curUser": curUser, 'accounts': accounts})

def loginPageView(request):
	request.user.is_authenticated
	if request.method == 'POST':


		# #4.bruteforce.better
		# if "potato" not in request.session:
		# 	request.session["potato"] = 0

		# if "lastpotato" not in request.session:
		# 	request.session["lastpotato"] = 0

		# curtime = time.time()
		# if request.session["lastpotato"] + 60 < curtime:
		# 	request.session["potato"] = 0

		# request.session["potato"] += 1
		# request.session["lastpotato"] = curtime
		
		# if request.session["potato"] > 5:
		# 	#5.logging.better
		# 	#log.info(f"Blocked POST from \"{get_client_ip(request)}\", reason: \"Too many requests.\"")

		# 	messages.success(request, ("Too many requests."))
		# 	return render(request ,"pages/login.html", {})
		# #######################################################



		username = request.POST.get("username")
		password = request.POST.get("password")
		bLogIn = request.POST.get("butn") == "Log In"
	
		#1.sqlinject.bad
		checkExists = len(User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{username}'")) > 0

		#1.sqlinject.better
		#checkExists = len(User.objects.raw("SELECT * FROM auth_user WHERE username = %s", [username])) > 0

		if checkExists:
			if bLogIn == False: ## create user + acc

				#5.logging.better
				#log.info(f"Create account request from \"{get_client_ip(request)}\" with username \"{username}\", failed: \"Account already exists.\"")
				
				messages.success(request, ("Account already exists."))
				return render(request ,"pages/login.html", {})
		else:
			if bLogIn: ## login + no acc

				#5.logging.better
				#log.info(f"Login attempt from \"{get_client_ip(request)}\" with username \"{username}\", failed: \"Account does not exist.\"")

				messages.success(request, ("Account does not exist, try creating a new account."))
				return render(request ,"pages/login.html", {})
			else: #create user + no acc

				#3.plaintxtpw.bad
				user = User.objects.create(username=username, password=password)
	
				#3.plaintxtpw.better
				#user = User.objects.create_user(username, None, password)

				user.save()

				account = Account.objects.create(user=user, balance=25)
				account.save()
				
				login(request, user)

				#5.logging.better
				#log.info(f"User from \"{get_client_ip(request)}\" created new account with username \"{username}\".")

				return redirect("/user/" + username)
		

		#3.plaintxtpw.bad
		user = User.objects.get(username=username)
		if user.password == password:
			login(request, user)

			#5.logging.better
			#log.info(f"Successful login attempt from \"{get_client_ip(request)}\" with username \"{username}\".")

			return redirect("/user/" + username)
	


		#3.plaintxtpw.better
		#user = authenticate(request, username=username, password=password)
		#
		# if user is not None:
		# 	login(request, user)
		#
		# 	#5.logging.better
		# 	#log.info(f"Succesful login attempt from \"{get_client_ip(request)}\" with username \"{username}\".")
		#
		# 	return redirect("/user/" + username)
		



		messages.success(request, ("Invalid password."))

		#5.logging.better
		log.info(f"Login attempt from \"{get_client_ip(request)}\" with username \"{username}\", failed: \"Invalid password.\"")

	return render(request ,"pages/login.html", {})

def logoutPageView(request):
	logout(request)
	return redirect("/")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip