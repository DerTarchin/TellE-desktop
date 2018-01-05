def update_media(url, model, update_fn, last_update):
    limit = 50
    page = 1
    pages_remaining = True
    changed = []

    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version' : '2',
        'trakt-api-key' : client_id
    }

    while pages_remaining:
        request_url = url.format(last_update, page, limit)
        response = requests.get(request_url, headers=headers)

        data = response.json()

        for media in data:
            changed.append(media["ids"]["trakt"])

        pages_remaining = (page < response.headers["X-Pagination-Page-Count"])

    changed_models = model.objects.filter(trakt_id__in=changed)

    for media in changed_models:
        update_fn(media.trakt_id)

def update_database():
    last_update = LastUpdate.get(name="admin")
    movie_url = "https://api-v2launch.trakt.tv/movies/updates/{0}?page={1}&limit={2}"
    show_url = "https://api-v2launch.trakt.tv/shows/updates/{0}?page={1}&limit={2}"

    update_media(movie_url, Movie, add_movie, strptime(last_update.date + datetime.timedelta(days=1), "%Y-%m-%d"))
    update_media(show_url, TVShow, add_show, strptime(last_update.date + datetime.timedelta(days=1), "%Y-%m-%d"))

    last_update.date = datetime.now()