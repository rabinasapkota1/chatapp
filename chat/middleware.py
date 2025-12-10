from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            # Create profile automatically if missing
            profile = getattr(request.user, "profile", None)
            if profile is None:
                from users.models import Profile
                Profile.objects.create(user=request.user)

            # Update last_seen safely
            request.user.profile.last_seen = timezone.now()
            request.user.profile.save(update_fields=["last_seen"])

        response = self.get_response(request)
        return response
