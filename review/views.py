from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm
from .models import Review, Venue
## from venues.models import Venue  
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def add_review(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            return redirect('venue_detail', venue_id=venue.id)
    else:
        form = ReviewForm()

    return render(request, 'review/add_review.html', {'form': form, 'venue': venue})