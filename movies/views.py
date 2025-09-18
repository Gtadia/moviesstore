from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = (
        Review.objects.filter(movie=movie, parent__isnull=True)
        .select_related('user')
        .prefetch_related('replies__user', 'replies__replies__user')
    )

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            movie = Movie.objects.get(id=id)
            review = Review()
            review.comment = comment
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('movies.show', id=id)
    return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            review.comment = comment
            review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


@login_required
def reply_review(request, id, review_id):
    movie = get_object_or_404(Movie, id=id)
    parent_review = get_object_or_404(Review, id=review_id, movie=movie)

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            Review.objects.create(
                comment=comment,
                movie=movie,
                user=request.user,
                parent=parent_review,
            )
    return redirect('movies.show', id=id)
