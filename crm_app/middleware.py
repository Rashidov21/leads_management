from django.shortcuts import redirect
from django.urls import reverse


class RoleMiddleware:
    """Middleware to check user roles and permissions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add user role to request
        if request.user.is_authenticated:
            request.user_role = request.user.role
        else:
            request.user_role = None
        
        response = self.get_response(request)
        return response

