from django.contrib import admin
from . models import Contact,User,Shoes,Wishlist,Cart,Transaction
# Register your models here.
admin.site.register(Contact)
admin.site.register(User)
admin.site.register(Shoes)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Transaction)