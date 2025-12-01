from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles and not request.user.is_admin:
                messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q.")
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to check if user is admin"""
    return role_required('admin')(view_func)


def manager_or_admin_required(view_func):
    """Decorator to check if user is manager or admin"""
    return role_required('admin', 'sales_manager')(view_func)

