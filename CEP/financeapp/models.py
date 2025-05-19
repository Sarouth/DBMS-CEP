from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_currency = models.CharField(max_length=3, default='USD')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('credit', 'Credit Card'),
        ('investment', 'Investment'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=20, default='#4299E1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.account_type})"

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=20, default='#F56565')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return f"{self.name} ({self.category_type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('debit', 'Debit Card'),
        ('credit', 'Credit Card'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Payment'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200)
    date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.description} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Update account balance when transaction is saved
        is_new = self.pk is None
        
        if not is_new:
            # Get the original transaction from the database
            old_transaction = Transaction.objects.get(pk=self.pk)
            old_amount = old_transaction.amount
            
            # Revert previous transaction effect
            if old_transaction.transaction_type == 'income':
                old_transaction.account.balance -= old_amount
            else:
                old_transaction.account.balance += old_amount
            
            old_transaction.account.save()
        
        # Apply new transaction effect
        if self.transaction_type == 'income':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        
        self.account.save()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Update account balance when transaction is deleted
        if self.transaction_type == 'income':
            self.account.balance -= self.amount
        else:
            self.account.balance += self.amount
            
        self.account.save()
        super().delete(*args, **kwargs)

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.name} Budget - {self.amount}"
    
    def get_spent_amount(self):
        """Calculate how much has been spent in this budget's category during budget period"""
        query = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='expense',
            date__gte=self.start_date
        )
        
        if self.end_date:
            query = query.filter(date__lte=self.end_date)
            
        return query.aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    def get_remaining(self):
        """Calculate remaining budget"""
        return self.amount - self.get_spent_amount()

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_percentage_complete(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100
