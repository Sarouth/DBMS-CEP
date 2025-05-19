from django.contrib import admin
from .models import UserProfile, Account, Category, Transaction, Budget, Goal

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_currency')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'balance', 'created_at')
    list_filter = ('account_type', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category_type')
    list_filter = ('category_type',)
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'account', 'category', 'amount', 'transaction_type', 'date')
    list_filter = ('transaction_type', 'date', 'account', 'category')
    search_fields = ('description', 'notes')
    date_hierarchy = 'date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'user', 'amount', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('category__name',)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_amount', 'target_date', 'get_percentage_complete')
    list_filter = ('target_date',)
    search_fields = ('name',)