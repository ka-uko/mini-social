from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Notification

@login_required
def inbox(request):
    qs = Notification.objects.filter(to_user=request.user).select_related('actor')
    return render(request, 'notify/inbox.html', {'items': qs})

@login_required
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, to_user=request.user)
    n.is_read = True
    n.save(update_fields=['is_read'])
    return redirect('notify_inbox')
