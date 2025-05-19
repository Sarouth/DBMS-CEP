from django.db.models import Sum
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Account, Category, Transaction, Budget, Goal
from .serializers import (
    UserProfileSerializer, RegisterSerializer, AccountSerializer,
    CategorySerializer, TransactionSerializer, BudgetSerializer, GoalSerializer
)

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(APIView):
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        queryset = Category.objects.filter(user=self.request.user)
        category_type = self.request.query_params.get('type', None)
        
        if category_type:
            queryset = queryset.filter(category_type=category_type)
            
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Apply filters
        account_id = self.request.query_params.get('account', None)
        category_id = self.request.query_params.get('category', None)
        transaction_type = self.request.query_params.get('type', None)
        date_range = self.request.query_params.get('date_range', None)
        
        if account_id and account_id != 'all':
            queryset = queryset.filter(account_id=account_id)
            
        if category_id and category_id != 'all':
            queryset = queryset.filter(category_id=category_id)
            
        if transaction_type and transaction_type != 'all':
            queryset = queryset.filter(transaction_type=transaction_type)
            
        if date_range:
            today = timezone.now().date()
            
            if date_range == 'month':
                start_date = today.replace(day=1)
                queryset = queryset.filter(date__gte=start_date)
            elif date_range == 'quarter':
                start_date = today - timedelta(days=90)
                queryset = queryset.filter(date__gte=start_date)
            elif date_range == 'year':
                start_date = today.replace(month=1, day=1)
                queryset = queryset.filter(date__gte=start_date)
        
        return queryset.order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).order_by('category__name')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).order_by('target_date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
def dashboard_summary(request):
    """Get summary data for the dashboard"""
    user = request.user
    
    # Get account totals
    accounts = Account.objects.filter(user=user)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Get monthly income and expenses
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    month_transactions = Transaction.objects.filter(
        user=user,
        date__gte=start_of_month,
        date__lte=today
    )
    
    income = month_transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = month_transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get recent transactions
    recent_transactions = TransactionSerializer(
        Transaction.objects.filter(user=user).order_by('-date')[:5],
        many=True
    ).data
    
    # Get spending by category
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    expense_categories = Category.objects.filter(user=user, category_type='expense')
    category_spending = []
    
    for category in expense_categories:
        amount = Transaction.objects.filter(
            user=user,
            category=category,
            transaction_type='expense',
            date__gte=start_of_month,
            date__lte=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if amount > 0:
            category_spending.append({
                'category': category.name,
                'color': category.color,
                'amount': amount
            })
    
    # Get monthly income/expense data for chart
    months = []
    income_data = []
    expense_data = []
    
    for i in range(6):
        # Get data for last 6 months
        end_date = timezone.now().date().replace(day=1) - timedelta(days=1) if i == 0 else months[-1]
        start_date = end_date.replace(day=1)
        
        month_name = start_date.strftime('%b')
        months.append(month_name)
        
        month_income = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        income_data.append(float(month_income))
        
        month_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_data.append(float(month_expenses))
    
    # Reverse lists to show chronological order
    months.reverse()
    income_data.reverse()
    expense_data.reverse()
    
    return Response({
        'total_balance': float(total_balance),
        'month_income': float(income),
        'month_expenses': float(expenses),
        'recent_transactions': recent_transactions,
        'category_spending': category_spending,
        'chart_data': {
            'months': months,
            'income': income_data,
            'expenses': expense_data
        }
    })