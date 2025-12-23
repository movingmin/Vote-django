import functools
from django.core.cache import cache
from django.shortcuts import render
from django.contrib import messages

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def ratelimit(key_prefix, limit=5, period=60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                ip = get_client_ip(request)
                key = f"ratelimit:{key_prefix}:{ip}"
                count = cache.get(key, 0)
                
                if count >= limit:
                    messages.error(request, "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
                    return render(request, 'index.html') # Or specific template depending on view
                
                cache.set(key, count + 1, period)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def class_ratelimit(key_prefix, limit=5, period=60):
    def decorator(cls):
        original_post = cls.post
        
        @functools.wraps(original_post)
        def wrapper(self, request, *args, **kwargs):
             if request.method == 'POST':
                ip = get_client_ip(request)
                key = f"ratelimit:{key_prefix}:{ip}"
                count = cache.get(key, 0)
                
                if count >= limit:
                    messages.error(request, f"요청이 너무 많습니다. {period}초 후에 다시 시도해주세요.")
                    # Determine where to redirect or render based on the view
                    if 'vote' in request.path:
                         return render(request, 'vote.html', {'message': 'Rate Limit Exceeded'})
                    return render(request, 'index.html')
                
                cache.set(key, count + 1, period)
             return original_post(self, request, *args, **kwargs)
        
        cls.post = wrapper
        return cls
    return decorator
