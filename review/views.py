from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm
from .models import Review
from main.models import Venue
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt


@login_required
def get_reviews_by_venue_json(request, venue_id):
    """Get all reviews for a specific venue in JSON format"""
    venue = get_object_or_404(Venue, id=venue_id)
    reviews = Review.objects.filter(venue=venue).select_related('user')
    
    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'id': review.id,
            'username': review.user.username,
            'venue_id': venue.id,
            'accessibility': review.accessibility,
            'facility': review.facility,
            'value_for_money': review.value_for_money,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
            'average_rating': review.average_rating(),
        })
    
    return JsonResponse(reviews_data, safe=False)


# Create your views here.
@login_required
def add_review(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    # Check if the user has already posted a review for this venue
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


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Vérifie que l'utilisateur est bien l'auteur
    if request.user != review.user:
        return JsonResponse({"success": False, "error": "Not allowed"}, status=403)
    venue_id = review.venue.id
    review.delete()
    return JsonResponse({"success": True, "review_id": review_id, "venue_id": venue_id})


def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Prevent editing a review by another user
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
    venues = Venue.objects.all().order_by('name')
    form = ReviewForm()
    return render(request, 'review/add_review_general.html', {
        'form': form, 
        'venues': venues
    })


@login_required
def add_review_with_ajax(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    # Vérifier si l'utilisateur a déjà posté une review
    existing_review = Review.objects.filter(user=request.user, venue=venue).first()
    if existing_review:
        return JsonResponse({
            "success": False,
            "error": f"You've already reviewed {venue.name}."
        }, status=400)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()

            return JsonResponse({
    "success": True,
    "username": request.user.username,
    "average_rating": review.average_rating(),  
    "accessibility": review.accessibility,
    "facility": review.facility,
    "value_for_money": review.value_for_money,
    "comment": review.comment,
    "venue_id": venue.id
})
        else:
            return JsonResponse({
                "success": False,
                "error": form.errors
            }, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def edit_review_ajax(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        
        if form.is_valid():
            form.save()
            review.refresh_from_db()
            return JsonResponse({
                "success": True,
                "username": request.user.username,
                "accessibility": review.accessibility,
                "facility": review.facility,
                "value_for_money": review.value_for_money,
                "comment": review.comment,
                "average_rating": review.average_rating(),
                "review_id": review.id,
                "venue_id": review.venue.id
            })
        print("EDIT REVIEW ERRORS:", form.errors)
        return JsonResponse({"success": False, "error": form.errors}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
@csrf_exempt  # Pour Flutter, on utilise csrf_exempt avec pbp_django_auth
def add_review_ajax_flutter(request, venue_id):
    """Version Flutter-compatible de add_review_ajax"""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)
    
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Vérifier si l'utilisateur a déjà posté une review
    existing_review = Review.objects.filter(user=request.user, venue=venue).first()
    if existing_review:
        return JsonResponse({
            "success": False,
            "error": f"You've already reviewed {venue.name}."
        }, status=400)
    
    try:
        # Récupérer les données du POST
        accessibility = int(request.POST.get('accessibility', 0))
        facility = int(request.POST.get('facility', 0))
        value_for_money = int(request.POST.get('value_for_money', 0))
        comment = request.POST.get('comment', '')
        
        # Validation
        if not all([1 <= accessibility <= 5, 1 <= facility <= 5, 1 <= value_for_money <= 5]):
            return JsonResponse({
                "success": False,
                "error": "Ratings must be between 1 and 5"
            }, status=400)
        
        # Créer la review
        review = Review.objects.create(
            user=request.user,
            venue=venue,
            accessibility=accessibility,
            facility=facility,
            value_for_money=value_for_money,
            comment=comment
        )
        
        return JsonResponse({
            "success": True,
            "review_id": review.id,
            "username": request.user.username,
            "average_rating": review.average_rating(),
            "accessibility": review.accessibility,
            "facility": review.facility,
            "value_for_money": review.value_for_money,
            "comment": review.comment,
            "venue_id": venue.id
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@login_required
@csrf_exempt
def edit_review_ajax_flutter(request, review_id):
    """Version Flutter-compatible de edit_review_ajax"""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)
    
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    try:
        # Récupérer les données
        accessibility = int(request.POST.get('accessibility', review.accessibility))
        facility = int(request.POST.get('facility', review.facility))
        value_for_money = int(request.POST.get('value_for_money', review.value_for_money))
        comment = request.POST.get('comment', review.comment)
        
        # Validation
        if not all([1 <= accessibility <= 5, 1 <= facility <= 5, 1 <= value_for_money <= 5]):
            return JsonResponse({
                "success": False,
                "error": "Ratings must be between 1 and 5"
            }, status=400)
        
        # Mettre à jour la review
        review.accessibility = accessibility
        review.facility = facility
        review.value_for_money = value_for_money
        review.comment = comment
        review.save()
        
        return JsonResponse({
            "success": True,
            "review_id": review.id,
            "username": request.user.username,
            "accessibility": review.accessibility,
            "facility": review.facility,
            "value_for_money": review.value_for_money,
            "comment": review.comment,
            "average_rating": review.average_rating(),
            "venue_id": review.venue.id
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@login_required
@csrf_exempt
def delete_review_flutter(request, review_id):
    """Version Flutter-compatible de delete_review"""
    review = get_object_or_404(Review, id=review_id)
    
    # Vérifier que l'utilisateur est bien l'auteur
    if request.user != review.user:
        return JsonResponse({"success": False, "error": "Not allowed"}, status=403)
    
    venue_id = review.venue.id
    review.delete()
    
    return JsonResponse({
        "success": True,
        "review_id": review_id,
        "venue_id": venue_id
    })