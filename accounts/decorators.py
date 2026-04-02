from functools import wraps

from django.shortcuts import redirect


def role_required(*roles):
    """Décorateur pour restreindre l'accès selon le rôle de l'utilisateur."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return redirect('accounts:dashboard')
        return wrapper
    return decorator
