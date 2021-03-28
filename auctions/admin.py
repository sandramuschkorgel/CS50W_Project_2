from django.contrib import admin

from .models import User, Listing, Category, Watchlist, Bid, Comment

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'starting_bid', 'status', 'user', 'date')

class BidAdmin(admin.ModelAdmin):
    list_display = ('listing', 'bidding', 'user', 'status', 'date')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('listing', 'comment')

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('get_listing', 'user')

    def get_listing(self, obj):
        return "\n".join([l.title for l in obj.item.all()])

admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Category)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
