from django.db import models
from django.utils import timezone

# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	message=models.TextField()


	def __str__(self):
		return self.name

class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	address=models.TextField()
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.fname+" - "+self.lname


class Shoes(models.Model):

	CHOICES=(
		('sports','sports'),
		('collection','collection'),
		('racingboots','racingboots')
		)
	seller=models.ForeignKey(User,on_delete=models.CASCADE)
	shoes_category=models.CharField(max_length=100,choices=CHOICES)
	shoes_name=models.CharField(max_length=100)
	shoes_price=models.IntegerField()
	shoes_quantity=models.IntegerField()
	shoes_image=models.ImageField(upload_to="shoes_images/")


def __str__(self):
	return self.seller.fname+" - "+self.shoes_name

class Wishlist(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	shoes=models.ForeignKey(Shoes,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.shoes.shoes_name



class Cart(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	shoes=models.ForeignKey(Shoes,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	qty=models.IntegerField(default=1)
	price=models.IntegerField()
	total_price=models.IntegerField()
	payment_status=models.CharField(max_length=100,default="pending")


	def __str__(self):
		return self.user.fname+" - "+self.shoes.shoes_name


class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)


