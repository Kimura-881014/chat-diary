from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email','username')

class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username','chat_type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','is_manager',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('user_id', 'username', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('user_id', 'username')
    ordering = ('user_id',)

admin.site.register(User, MyUserAdmin)
