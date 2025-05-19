from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Account, Category, Transaction, Budget, Goal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'preferred_currency')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    preferred_currency = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'preferred_currency')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        preferred_currency = validated_data.pop('preferred_currency')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, preferred_currency=preferred_currency)
        return user

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'account_type', 'balance', 'account_number', 'color', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type', 'color', 'created_at')
        read_only_fields = ('id', 'created_at')

class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    category_color = serializers.ReadOnlyField(source='category.color')
    
    class Meta:
        model = Transaction
        fields = ('id', 'account', 'account_name', 'category', 'category_name', 'category_color', 
                  'amount', 'transaction_type', 'description', 'date', 'payment_method', 
                  'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'account_name', 'category_name', 'category_color')

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_color = serializers.ReadOnlyField(source='category.color')
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = ('id', 'category', 'category_name', 'category_color', 'amount', 
                  'spent_amount', 'remaining_amount', 'percentage_used',
                  'start_date', 'end_date', 'created_at')
        read_only_fields = ('id', 'created_at', 'spent_amount', 'remaining_amount', 'percentage_used', 
                           'category_name', 'category_color')
    
    def get_spent_amount(self, obj):
        return obj.get_spent_amount()
    
    def get_remaining_amount(self, obj):
        return obj.get_remaining()
    
    def get_percentage_used(self, obj):
        if obj.amount == 0:
            return 0
        return (obj.get_spent_amount() / obj.amount) * 100

class GoalSerializer(serializers.ModelSerializer):
    percentage_complete = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = ('id', 'name', 'target_amount', 'current_amount', 'target_date', 
                  'percentage_complete', 'created_at')
        read_only_fields = ('id', 'created_at', 'percentage_complete')
    
    def get_percentage_complete(self, obj):
        return obj.get_percentage_complete()
