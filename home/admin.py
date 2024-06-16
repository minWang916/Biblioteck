from django.contrib import admin
from .models import *

# Register your models here.
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', "publisher", "language", "codeISBN")

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", 'username', "email")

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", 'bookID', 'userID', 'rating', 'created_at')

class BorrowanceAdmin(admin.ModelAdmin):
    list_display = ('id', "copyID", "userID", "status")

class CopyAdmin(admin.ModelAdmin):
    list_display = ('id', "bookID", "userID")

class ModAppAdmin(admin.ModelAdmin):
    list_display = ("applicant", "status", "created_at")

class ThoughtAdmin(admin.ModelAdmin):
    list_display = ("userID", "thought", "created_at")

admin.site.register(Book, BookAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Borrowance, BorrowanceAdmin)
admin.site.register(Copy, CopyAdmin)
admin.site.register(ModApplication, ModAppAdmin)
admin.site.register(Thought, ThoughtAdmin)