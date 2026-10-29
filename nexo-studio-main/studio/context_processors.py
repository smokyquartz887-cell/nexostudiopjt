from .models import Business

def business_context(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'available_businesses': [], 'active_business_id': None}
    businesses = Business.objects.filter(owner=request.user).order_by('name')
    active_id = request.session.get('active_business_id')
    if not businesses.filter(pk=active_id).exists():
        active_id = businesses.first().pk if businesses.exists() else None
    return {'available_businesses': businesses, 'active_business_id': active_id}
