from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm
from .models import Review, Venue
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def add_review(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    # Vérifie si l'utilisateur a déjà posté une review pour cette venue
    existing_review = Review.objects.filter(user=request.user, venue=venue).first()
    if existing_review:
        messages.warning(request, f"You've already reviewed {venue.name}.")
        return redirect('main:show_venue', id=venue.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            messages.success(request, f"Your review for {venue.name} was added successfully!")
            return redirect('main:show_venue', id=venue.id)
    else:
        form = ReviewForm()

    return render(request, 'review/add_review.html', {'form': form, 'venue': venue})


def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # (optionnel) Vérifie que seul l’auteur peut supprimer sa review :
    if request.user != review.user:
        return redirect('main:show_venue', id=review.venue.id)

    review.delete()
    return redirect('main:show_venue', id=review.venue.id)

def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # (optionnel) Empêche la modification d'une review d'un autre utilisateur
    if request.user != review.user:
        return redirect('main:show_venue', id=review.venue.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('main:show_venue', id=review.venue.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review/edit_review.html', {'form': form, 'review': review})

def add_review_general(request):
    if request.method == 'POST':
        venue_id = request.POST.get('venue')
        venue = get_object_or_404(Venue, id=venue_id)

        # Vérifie si l'utilisateur a déjà laissé une review pour cette venue
        existing_review = Review.objects.filter(user=request.user, venue=venue).first()
        if existing_review:
            messages.warning(request, f"You've already reviewed {venue.name}.")
            return redirect('main:show_venue', id=venue.id)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            messages.success(request, f"Your review for {venue.name} was added successfully!")
            return redirect('main:show_venue', id=venue.id)
    else:
        form = ReviewForm()

    venues = Venue.objects.all()
    return render(request, 'review/add_review_general.html', {'form': form, 'venues': venues})

