from django.shortcuts import render, redirect
from . models import Contact,User,Shoes,Wishlist,Cart,Transaction
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.mail import send_mail
import random
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

def validate_email(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	print(data)
	return JsonResponse(data)


def validate_email_signup(request):
	email=request.GET.get('email')
	print(email)
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	print(data)
	return JsonResponse(data)

	
def initiate_payment(request):
    try:
        amount = int(request.POST['amount'])
        user=User.objects.get(email=request.session['email'])
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str("mukeshsarva07@gmail.com")),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts=Cart.objects.filter(user=user)
    for i in carts:
    	i.payment_status="completed"
    	i.save()
    carts=Cart.objects.filter(user=user,payment_status="pending")
    request.session['cart_count']=len(carts)

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html') 

def contact(request): 
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			mobile=request.POST['mobile'],
			email=request.POST['email'],
			message=request.POST['message']
			)
		msg="Contact Saved Successfully"
		contacts=Contact.objects.all().order_by("-id")[:5]
		
		return render(request,'contact.html',{'msg':msg,'contacts':contacts}) 

	else:
		contacts=Contact.objects.all().order_by("-id")[:5]
		
		return render(request,'contact.html',{'contacts':contacts}) 

def shoes(request):
	return render(request,'shoes.html')  


def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						cpassword =request.POST['cpassword'],
						usertype=request.POST['usertype']
					)
				msg="SignUp Successfull"
				return render(request,'login.html',{'msg':msg}) 
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')


def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
					email=request.POST['email'],
					password=request.POST['password']
				)
			if user.usertype=="user":
				request.session['email']=user.email
				request.session['fname']=user.fname
				wishlists=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user)
				request.session['cart_count']=len(carts)
				return render(request,'index.html')
			
			elif user.usertype=="seller":
				request.session['email']=user.email
				request.session['fname']=user.fname
				return render(request,'seller_index.html')
		except:
			msg="Email Or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:

			return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['wishlist_count']
		return render(request,'login.html')
	except:
		return render(request,'login.html')


def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])

		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.cpassword=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="Password & Confirm New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')



def seller_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])

		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.cpassword=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="Password & Confirm New Password Does Not Matched"
				return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'seller_change_password.html',{'msg':msg})
	else:
		return render(request,'seller_change_password.html')




def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			subject = 'OTP For Forgot Password'
			otp=random.randint(1000,9999)
			message = 'Your OTP For Forgot Password Is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [request.POST['email'], ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':request.POST['email']})
		except:
			msg="Email Does Not Exists"
			return render(request,'forgot_password.html',{'msg':msg})
	else:	
		return render(request,'forgot_password.html')


def verify_otp(request):
	otp1=request.POST['otp1']
	otp2=request.POST['otp2']
	email=request.POST['email']

	if otp1==otp2:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'otp':otp1,'email':email,'msg':msg})


def new_password(request):
	email=request.POST['email']	
	new_password=request.POST['new_password']
	cnew_password=request.POST['cnew_password']

	user=User.objects.get(email=email)

	if new_password==cnew_password:
		user.password=new_password
		user.cpassword=new_password
		user.save()
		msg="Password Updated Successfully"
		return render(request,'login.html',{'msg':msg})

	else:
		msg="New Password & Confirm New Password Does Not Matched"
		return render(request,'new_password.html',{'email':email,'msg':msg})
	


def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		user.save()
		msg="Profile Update Successfully"
		return render(request,'index.html')
	else:
		return render(request,'profile.html',{'user':user})



def seller_profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		user.save()
		msg="Profile Update Successfully"
		return render(request,'seller_index.html')
	else:
		return render(request,'seller_profile.html',{'user':user})


def seller_add_shoes(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Shoes.objects.create(
				seller=seller,
				shoes_category=request.POST['shoes_category'],
				shoes_name=request.POST['shoes_name'],
				shoes_price=request.POST['shoes_price'],
				shoes_quantity=request.POST['shoes_quantity'],
				shoes_image=request.FILES['shoes_image']
			)
		msg="Shoes Added Successfully"
		return render(request,'seller_add_shoes.html',{'msg':msg})
	else:	
		return render(request,'seller_add_shoes.html')
	


def seller_view_shoes(request):
	seller=User.objects.get(email=request.session['email'])
	shoes=Shoes.objects.filter(seller=seller)

	return render(request,'seller_view_shoes.html',{'shoes':shoes})


def seller_shoes_detail(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	return render(request,'seller_shoes_detail.html',{'shoes':shoes})



def seller_shoes_edit(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	print(shoes)
	if request.method=="POST":
		print("POST CAlled")
		shoes.shoes_name=request.POST['shoes_name']	
		shoes.shoes_price=request.POST['shoes_price']
		shoes.shoes_author=request.POST['shoes_quantity']
		try:
			shoes.shoes_image=request.FILES['shoes_image']
		except:
			pass
		shoes.save()
		return redirect("seller_view_shoes")
	else:
		return render(request,'seller_shoes_edit.html',{'shoes':shoes})


def seller_shoes_delete(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	shoes.delete()
	return redirect("seller_view_shoes")


def user_view_shoes(request,cs):
	if cs=="all":
		shoes=Shoes.objects.all()
		return render(request,'user_view_shoes.html',{'shoes':shoes})
	else:
		shoes=Shoes.objects.filter(shoes_name=cs)
		return render(request,'user_view_shoes.html',{'shoes':shoes})


def user_shoes_detail(request,pk):
	flag=False
	flag1=False
	shoes=Shoes.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	try:
		Wishlist.objects.get(user=user,shoes=shoes)
		flag=True
	except:
		pass

	try:
		Cart.objects.get(user=user,shoes=shoes,payment_status="pending")
		flag1=True
	except:
		pass
	return render(request,'user_shoes_detail.html',{'shoes':shoes,'flag':flag,'flag1':flag1})


def add_to_wishlist(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,shoes=shoes)
	return redirect('mywishlist')


def mywishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'mywishlist.html',{'wishlists':wishlists})



def remove_from_wishlist(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.get(user=user,shoes=shoes)
	wishlists.delete()
	return redirect('mywishlist')



def add_to_cart(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,shoes=shoes,price=shoes.shoes_price,total_price=shoes.shoes_price)
	return redirect('mycart')


def mycart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'mycart.html',{'carts':carts,'net_price':net_price})



def remove_from_cart(request,pk):
	shoes=Shoes.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.get(user=user,shoes=shoes)
	carts.delete()
	return redirect('mycart')


def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	qty=int(request.POST['qty'])
	cart.qty=qty
	cart.total_price=qty*cart.price
	cart.save()
	return redirect('mycart')