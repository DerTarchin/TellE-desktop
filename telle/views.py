from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from datetime import datetime
from django.utils import formats
import json

from telle.models import *
from telle.forms import *
from canistreamit import *

import requests, time
from time import *
import json
from django.core.cache import caches
from lookup import *
from django.db import transaction
from hashlib import sha1 as sha_constructor
from sorting import *
import urllib

from xml.etree import ElementTree
from djutils.decorators import async
from django.db.models import Q

from pprint import pprint

from api_lookup import *

client_secret = "bdefb06b693036f65546bfda2172fcaadb59c20318cf8c5360d96a920cd2e428"
client_id = "10f2b8848e81cad86d5515b87221a59b771f088bb6b5d31ae33d6c6478aac658"
redirect_uri = "http://localhost:8000/token"

SEARCH_CACHE = caches['default']

# TODO: Change for actual running
CACHE_TIMEOUT = None

@login_required
def movie_info_page(request, trakt_id):
    if request.method != "GET":
        return HttpResponseRedirect(reverse("movies"))

    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version' : '2',
        'trakt-api-key' : client_id
    }

    tag = "movie-people-{0}".format(trakt_id)
    cached = SEARCH_CACHE.get(tag)

    if cached:
        movie_people = json.loads(cached)
    else:
        url = 'https://api-v2launch.trakt.tv/movies/{0}/people?extended=images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        try:
            movie_people = result.json()
            SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
        except:
            return home(request)
        

    crew_dict = movie_people.get('crew', {})
    full_crew = []
    full_crew += crew_dict.get('directing', [])
    full_crew += crew_dict.get('production', [])
    full_crew += crew_dict.get('writing', [])
    full_crew += crew_dict.get('camera', [])
    full_crew += crew_dict.get('art', [])
    full_crew += crew_dict.get('costume & make-up', [])
    full_crew += crew_dict.get('sound', [])
    full_crew += crew_dict.get('crew', [])

    movie_people['crew'] = full_crew

    try:
        movie_info = Movie.objects.get(trakt_id=trakt_id)
    except Movie.DoesNotExist:
        # Get from the API and add the expected fields
        movie_info = get_full_movie(trakt_id, SEARCH_CACHE, CACHE_TIMEOUT)
        movie_info["genre_set"] = {}
        movie_info["genre_set"]["all"] = movie_info["genres"]
        movie_info["fanart_url"] = movie_info["images"]["fanart"]["thumb"]
        movie_info["poster_url"] = movie_info["images"]["poster"]["medium"]

    #     #TEMP API
    # a_movie = cani_search('V for Vendetta')[0]
    # availability = [streaming(a_movie['_id']), rental(a_movie['_id']), purchase(a_movie['_id']), 
    #                                             dvd(a_movie['_id']), xfinity(a_movie['_id'])]

    context = {
        # "temp_available": availability,
        "media_info": movie_info,
        "media_people": movie_people
    }
    return render(request, 'movie_info.html', context)

@login_required
def show_info_page(request, trakt_id):
    if request.method != "GET":
        return HttpResponseRedirect(reverse("shows"))

    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version' : '2',
        'trakt-api-key' : client_id
    }

    tag = "show-people-{0}".format(trakt_id)
    cached = SEARCH_CACHE.get(tag)

    if cached:
        show_people = json.loads(cached)
    else:
        url = 'https://api-v2launch.trakt.tv/shows/{0}/people?extended=images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        try:
            show_people = result.json()
            SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
        except:
            return home(request)

    crew_dict = show_people.get('crew', {})
    full_crew = []
    full_crew += crew_dict.get('directing', [])
    full_crew += crew_dict.get('production', [])
    full_crew += crew_dict.get('writing', [])
    full_crew += crew_dict.get('camera', [])
    full_crew += crew_dict.get('art', [])
    full_crew += crew_dict.get('costume & make-up', [])
    full_crew += crew_dict.get('sound', [])
    full_crew += crew_dict.get('crew', [])

    show_people['crew'] = full_crew

    try:
        show_info = TVShow.objects.get(trakt_id=trakt_id)
        show_user = UserTVShow.objects.get(trakt_id=trakt_id)
        show_seasons = None
    except TVShow.DoesNotExist, UserTVShow.DoesNotExist:
        show_info = get_full_show(trakt_id, SEARCH_CACHE, CACHE_TIMEOUT)
        show_info["showgenre_set"] = {}
        show_info["showgenre_set"]["all"] = show_info["genres"]
        show_info["fanart_url"] = show_info["images"]["fanart"]["thumb"]
        show_info["poster_url"] = show_info["images"]["poster"]["medium"]
        show_info["poster_url"] = show_info["images"]["poster"]["medium"]
        show_info["poster_url"] = show_info["images"]["poster"]["medium"]

        show_user = None

        tag = "episodes-{0}".format(trakt_id)
        cached = SEARCH_CACHE.get(tag)
        
        if cached:
            show_seasons = json.loads(cached)
        else:
            url = 'https://api-v2launch.trakt.tv/shows/{0}/seasons?extended=episodes,images,full'.format(trakt_id)
            result = requests.get(url, headers=headers)

            try:
                show_seasons = result.json()
                SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
            except:
                return home(request)
            

        show_seasons[:] = [d for d in show_seasons if d.get('number') != 0]
        for season in show_seasons:
            for episode in season['episodes']:
                if episode['first_aired'] and episode['first_aired'] != "None":
                    formatted = strptime(episode['first_aired'][:10],"%Y-%m-%d")
                    episode['first_aired'] = datetime.fromtimestamp(mktime(formatted))

    context = {
        "media_info": show_info,
        "media_people": show_people,
        "show_user": show_user,
        "show_seasons": show_seasons
    }
    return render(request, 'show_info.html', context)

@login_required
def person_info_page(request, trakt_id):
    if request.method != "GET":
        return home(request)

    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version' : '2',
        'trakt-api-key' : client_id
    }

    tag = "people-{0}".format(trakt_id)
    cached = SEARCH_CACHE.get(tag)

    if cached:
        person_info = json.loads(cached)
    else:
        url = 'https://api-v2launch.trakt.tv/people/{0}?extended=full,images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        try:
            person_info = result.json()
            SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
        except:
            return home(request)

    if person_info['birthday'] != None:
        formatted = strptime(person_info['birthday'],"%Y-%m-%d")
        person_info['birthday'] = datetime.fromtimestamp(mktime(formatted))
    if person_info['death'] != None:
        formatted = strptime(person_info['death'],"%Y-%m-%d")
        person_info['death'] = datetime.fromtimestamp(mktime(formatted))

    tag = "people-movies-{0}".format(trakt_id)
    cached = SEARCH_CACHE.get(tag)

    if cached:
        person_movies = json.loads(cached)
    else:
        url = 'https://api-v2launch.trakt.tv/people/{0}/movies?extended=images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        try:
            person_movies = result.json()
            SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
        except:
            return home(request)
    
    movies_dict = person_movies.get('crew', {})
    full_movies = []
    full_movies += person_movies.get('cast', {})
    full_movies += movies_dict.get('directing', [])
    full_movies += movies_dict.get('production', [])
    full_movies += movies_dict.get('writing', [])
    full_movies += movies_dict.get('camera', [])
    full_movies += movies_dict.get('art', [])
    full_movies += movies_dict.get('costume & make-up', [])
    full_movies += movies_dict.get('sound', [])
    full_movies += movies_dict.get('crew', [])
    person_movies = full_movies

    tag = "people-shows-{0}".format(trakt_id)
    cached = SEARCH_CACHE.get(tag)

    if cached:
        person_shows = json.loads(cached)
    else:
        url = 'https://api-v2launch.trakt.tv/people/{0}/shows?extended=images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        try:
            person_shows = result.json()
            SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
        except:
            return home(request)

    show_dict = person_shows.get('crew', {})
    full_shows = []
    full_shows += person_shows.get('cast', [])
    full_shows += show_dict.get('directing', [])
    full_shows += show_dict.get('production', [])
    full_shows += show_dict.get('writing', [])
    full_shows += show_dict.get('camera', [])
    full_shows += show_dict.get('art', [])
    full_shows += show_dict.get('costume & make-up', [])
    full_shows += show_dict.get('sound', [])
    full_shows += show_dict.get('crew', [])
    person_shows = full_shows

    context = {
        "person_info": person_info,
        "person_movies": person_movies,
        "person_shows": person_shows
    }
    return render(request, 'person_info.html', context)

####### CHECKED TO HERE #######
@login_required
@transaction.atomic
def manage_episode(request):
    response_text = {
        "error" : False,
        "error_messages" : []
    }

    trakt_id = request.POST["trakt_id"]
    episode = request.user.userepisode_set.get(trakt_id=trakt_id)

    season_number = episode.season.season.season_number
    episode_number = episode.episode.episode_number

    if episode.watched:
        
        request.user.usertvseason_set.filter(season__season_number__gte=season_number).update(watched=False)
        episode_query = (Q(season__season__season_number=season_number) & Q(episode__episode_number__gte=episode_number)) | Q(season__season__season_number__gt=season_number)
        request.user.userepisode_set.filter(episode_query).update(watched=False)

        show = episode.season.show

        containing_list = List.objects.filter(user=request.user, name__in=["watched", "to-watch"], tv_shows__trakt_id=show.trakt_id)

        if containing_list.exists():
            containing_list[0].tv_shows.remove(show)
            # containing_list[0].save()

            List.objects.get(user=request.user, name="watching").tv_shows.add(show)
    else:
        request.user.usertvseason_set.filter(season__season_number__lte=season_number).update(watched=True)
        episode_query = (Q(season__season__season_number=season_number) & Q(episode__episode_number__lte=episode_number)) | Q(season__season__season_number__lt=season_number)
        request.user.userepisode_set.filter(episode_query).update(watched=True)

        show = episode.season.show

        containing_list = List.objects.filter(user=request.user, name__in=["watched", "to-watch"], tv_shows__trakt_id=show.trakt_id)

        if containing_list.exists():
            containing_list[0].tv_shows.remove(show)
            # containing_list[0].save()

            List.objects.get(user=request.user, name="watching").tv_shows.add(show)

    # TODO: HANDLE OFF AIR AND OTHER STATUSES

    return HttpResponse(json.dumps(response_text), content_type='application/json')

@login_required
@transaction.atomic
def manage_season(request):
    response_text = {
        "error" : False,
        "error_messages" : []
    }

    trakt_id = request.POST["trakt_id"]
    season = request.user.usertvseason_set.get(trakt_id=trakt_id)

    if season.watched:
        request.user.usertvseason_set.filter(season__season_number__gte=season.season.season_number).update(watched=False)
        request.user.userepisode_set.filter(episode__season__season_number__gte=season.season.season_number).update(watched=False)

        show = season.show

        containing_list = List.objects.filter(user=request.user, name__in=["watched", "to-watch"], tv_shows__trakt_id=show.trakt_id)

        if containing_list.exists():
            containing_list[0].tv_shows.remove(show)
            # containing_list[0].save()

            List.objects.get(user=request.user, name="watching").tv_shows.add(show)
    else:
        request.user.usertvseason_set.filter(season__season_number__lte=season.season.season_number).update(watched=True)
        request.user.userepisode_set.filter(episode__season__season_number__lte=season.season.season_number).update(watched=True)

        show = season.show

        containing_list = List.objects.filter(user=request.user, name__in=["watched", "to-watch"], tv_shows__trakt_id=show.trakt_id)

        if containing_list.exists():
            containing_list[0].tv_shows.remove(show)
            # containing_list[0].save()

            List.objects.get(user=request.user, name="watching").tv_shows.add(show)

    # TODO: HANDLE OFF AIR AND OTHER STATUSES

    return HttpResponse(json.dumps(response_text), content_type='application/json')

@transaction.atomic
def delete_account(request):
    if request.user.is_authenticated():
        username = request.user.username
        auth_logout(request)
        User.objects.get(username=username).delete()
    return HttpResponseRedirect(reverse("register"))

@transaction.atomic
# @async
def get_episodes_async(user_show, show, user):
    trakt_id = show.trakt_id

    # Get all episodes and seasons
    url = "https://api-v2launch.trakt.tv/shows/{0}/seasons?extended=episodes,images,full".format(trakt_id)
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version' : '2',
        'trakt-api-key' : client_id
    }

    tag = "episodes-{0}".format(trakt_id)
    cached = SEARCH_CACHE.get(tag)
    if cached:
        result = json.loads(cached)       
    else:
        response = requests.get(url, headers=headers)

        try:
            result = response.json()
            SEARCH_CACHE.set(tag, response.text, CACHE_TIMEOUT)
        except:
            return False

    result[:] = [d for d in result if d.get('number') != 0]
    for season in result:
        new_season, _ = TVSeason.objects.update_or_create(trakt_id=season["ids"]["trakt"],
                                                          season_number=season["number"],
                                                          show=show,
                                                          poster_url=season["images"]["poster"]["medium"],
                                                          thumb_url=season["images"]["thumb"]["full"],
                                                          overview=season.get("overview", ""))
        new_season.save()

        user_season, _ = UserTVSeason.objects.update_or_create(user=user,
                                                               trakt_id=season["ids"]["trakt"],
                                                               season=new_season,
                                                               show=user_show)
        user_season.save()

        for episode in season["episodes"]:
            if episode['first_aired'] and episode['first_aired'] != "None":
                formatted = strptime(episode['first_aired'][:10],"%Y-%m-%d")
                episode['first_aired'] = datetime.fromtimestamp(mktime(formatted))

            new_episode, _ = Episode.objects.update_or_create(trakt_id=episode["ids"]["trakt"],
                                                              episode_number=episode["number"],
                                                              title=episode["title"],
                                                              season=new_season,
                                                              first_aired=episode["first_aired"],
                                                              screenshot_url=episode["images"]["screenshot"]["thumb"],
                                                              overview=episode.get("overview", ""))
            new_episode.save()

            user_episode, _ = UserEpisode.objects.update_or_create(user=user,
                                                                   trakt_id=episode["ids"]["trakt"],
                                                                   episode=new_episode,
                                                                   season=user_season)
            user_episode.save()
    return True

@login_required
@transaction.atomic
def manage_list(request):
    response_text = {
        "error" : True,
        "error_messages" : ["Request was not a post."]
    }
    print("HERE")
    if request.method == "POST":
        form = ManageListForm(request.POST)

        if form.is_valid():
            trakt_id = form.cleaned_data["trakt_id"]
            name = form.cleaned_data["name"]

            list_model = get_list(user=request.user, name=name)
            
            if not list_model:
                form.add_error("name", "List does not exist")
            else:
                media, media_type = get_movie_or_show(user=request.user, trakt_id=trakt_id)
                to_delete = get_from_list(list_model, trakt_id, media_type)

                if media_type == "movie":
                    content_field = "movies"
                elif media_type == "show":
                    content_field = "tv_shows"
                else:
                    # Lookup the movie information
                    # Get all episodes
                    # TODO
                    pass

                if to_delete:
                    if name in ["watched", "to-watch", "watching"]:
                        form.add_error("name", "Movie must be in a core list")
                    else:
                        getattr(list_model, content_field).remove(media)
                        list_model.save()
                        response_text["error"] = False
                else:
                    if name in ["watched", "to-watch", "watching"]:
                        defaults = { list_obj.name : list_obj for list_obj in List.objects.filter(user=request.user,
                                                                                                  type="default") }
                        if (getattr(defaults["watched"], content_field).filter(trakt_id=trakt_id).exists()):
                            getattr(defaults["watched"], content_field).remove(media)
                            defaults["watched"].save()
                        elif (getattr(defaults["to-watch"], content_field).filter(trakt_id=trakt_id).exists()):
                            getattr(defaults["to-watch"], content_field).remove(media)
                            defaults["to-watch"].save()
                        elif (getattr(defaults["watching"], content_field).filter(trakt_id=trakt_id).exists()):
                            getattr(defaults["watching"], content_field).remove(media)
                            defaults["watching"].save()

                    getattr(list_model, content_field).add(media)
                    list_model.save()
                    response_text["error"] = False

        response_text["error_messages"] = form.errors

    return HttpResponse(json.dumps(response_text), content_type='application/json')

@login_required
@transaction.atomic
def remove_media(request):
    # TODO: Handle exclusive Watching list
    response_text = {
        "error" : True,
        "error_messages" : ["Request was not a post"]
    }

    if request.method == "POST":
        trakt_id = request.POST["trakt_id"]
        media, media_type = get_movie_or_show(user=request.user, trakt_id=trakt_id)

        if media:
            if media_type == "movie":
                lists = List.objects.filter(user=request.user,movies__trakt_id=trakt_id)
                remove_from = "movies"
            else:
                lists = List.objects.filter(user=request.user,tv_shows__trakt_id=trakt_id)
                remove_from = "tv_shows"

            for l in lists:
                getattr(l, remove_from).remove(media)
                l.save()
            response_text["error_messages"] = []
            response_text["error"] = False;
        else:
            response_text["error_messages"] = ["No content with that trakt_id"]

    return HttpResponse(json.dumps(response_text), content_type='application/json')

@transaction.atomic
def add_movie(trakt_id):
    movie_info = get_full_movie(trakt_id, SEARCH_CACHE, CACHE_TIMEOUT)

    # TODO: Is not handling default values for certification for example
    movie, _ = Movie.objects.update_or_create(trakt_id=trakt_id,
                                              title=movie_info["title"],
                                              released=movie_info["released"],
                                              poster_url=movie_info.get("images", {}).get("poster", {}).get("medium", ""),
                                              fanart_url=movie_info.get("images", {}).get("fanart", {}).get("medium", ""),
                                              overview=movie_info.get("overview", ""),
                                              runtime=movie_info.get("runtime", None),
                                              certification=movie_info.get("certification", None))
    movie.save()

    for genre in movie_info["genres"]:
        g, _ = Genre.objects.update_or_create(movie=movie, genre=genre)
        g.save()

    return movie

@transaction.atomic
def add_show(trakt_id):
    show_info = get_full_show(trakt_id, SEARCH_CACHE, CACHE_TIMEOUT)

    # TODO: Is not handling default values for certification for example
    show, _ = TVShow.objects.update_or_create(trakt_id=trakt_id,
                                              title=show_info["title"],
                                              first_aired=show_info["first_aired"],
                                              poster_url=show_info.get("images", {}).get("poster", {}).get("medium", ""),
                                              fanart_url=show_info.get("images", {}).get("fanart", {}).get("medium", ""),
                                              overview=show_info.get("overview", ""),
                                              status=show_info.get("status", ""),
                                              airs=show_info.get("airs", ""),
                                              network=show_info.get("network", ""),
                                              certification=show_info.get("certification", "NR"))
    show.save()

    for genre in show_info["genres"]:
        g, _ = ShowGenre.objects.update_or_create(show=show, genre=genre)
        g.save()

    return show

@login_required
@transaction.atomic
def add_media(request):
  # TODO: Handle exclusive Watching list
  context = {
    #TODO: Is this form correct
    "list_form" : AddListForm()
  }

  if request.method != "POST":
    # TODO: Return back to search page
    # TODO: Maybe use ajax for this
    return render(request, "search.html", context)

  trakt_id = request.POST["trakt_id"]
  content_type = request.POST["type"]

  # TODO: Make general type argument
  watchlist = List.objects.get(user=request.user,name="to-watch")
  if content_type == "movie":
    movie = add_movie(trakt_id)
    watchlist.movies.add(movie)
  elif content_type == "show":
    show = add_show(trakt_id)
    user_show = UserTVShow(user=request.user, trakt_id=trakt_id, show=show)
    user_show.save()
    watchlist.tv_shows.add(user_show)
    get_episodes_async(user_show, show, request.user)
    print "DONE ADDING"
    
  watchlist.save()

  response_text = {
    'error': 0
  }

  return HttpResponse(json.dumps(response_text), content_type='application/json')
######### CHECKED TO HERE FROM BOTTOM ###########
@transaction.atomic
def register(request):
    context = {
        "register_form" : RegisterForm()
    }

    if request.method != "POST":
        return render(request, "register.html", context)

    form = RegisterForm(request.POST)
    context["register_form"] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, "register.html", context)

    new_user = User.objects.create_user(username=form.cleaned_data["email"],
                                        email=form.cleaned_data["email"],
                                        first_name=form.cleaned_data["first_name"],
                                        password=form.cleaned_data["password"])
    new_user.save()

    new_settings = Settings(user=new_user)
    new_settings.save()

    # Create default lists
    watch_list = List(user=new_user,name="favorites",pretty_name="Favorites",type="default")
    watch_list.save()
    watch_list = List(user=new_user,name="to-watch",pretty_name="To Watch",type="default")
    watch_list.save()
    watch_list = List(user=new_user,name="watching",pretty_name="Watching",type="default")
    watch_list.save()
    watch_list = List(user=new_user,name="watched",pretty_name="Watched",type="default")
    watch_list.save()

    new_user = authenticate(username=form.cleaned_data["email"],
                            password=form.cleaned_data["password"])
    auth_login(request, new_user)

    # Redirect to home
    return home(request)

@login_required
@transaction.atomic
def update_settings(request):
    user = request.user
    settings = request.user.settings

    if request.method == "POST":
        user_form = UserForm(request.POST, user=user)
        settings_form = SettingsForm(request.POST, user=request.user, instance=settings)
        settings_form.errors.update(user_form.errors)

        user_valid = user_form.is_valid()
        settings_valid = settings_form.is_valid()

        if user_valid and settings_valid:
            email = user_form.cleaned_data["email"]

            if user.username != email:
                user.username = email
                user.email = email
                user.save()
            settings_form.save()

    return home(request)

@login_required
def home(request):
    return HttpResponseRedirect(reverse(request.user.settings.home_page))

@login_required
def admin(request):
    return render(request, "admin.html", {})

@login_required
def clear_cache(request):
    SEARCH_CACHE.clear()
    return HttpResponseRedirect(reverse('admin'))

@login_required
@transaction.atomic
def delete_list(request):
    response_text = {
        "error" : True,
        "error_messages" : ["Request was not a post"]
    }

    if request.method == "POST":
        form = DeleteListForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            list_model = get_list(request.user, name)
            
            if not list_model:
                form.add_error("name", "List does not exist")
            elif list_model.type == "default":
                form.add_error("name", "Cannot delete default list")
            else:
                list_model.delete()
                response_text["error"] = False

        response_text["error_messages"] = form.errors

    return HttpResponse(json.dumps(response_text), content_type='application/json')

@login_required
@transaction.atomic
def add_list(request):
    response_text = {
        "error" : True,
        "error_messages" : ["Request was not a post"]
    }
    blacklist = ["nopadding","col-xs-2","col-xs-4","filter-item","poster","fanart"]

    if request.method == "POST":
        form = AddListForm(request.POST)

        if form.is_valid():
            pretty_name = form.cleaned_data["pretty_name"]
            key_name = pretty_name.lower().replace(" ", "-")
            watch_list = get_list(request.user, key_name)
            
            if watch_list != None:
                form.add_error("pretty_name", "List already exists")
            elif key_name in blacklist:
                form.add_error("pretty_name", "Invalid listname")
            else:
                watch_list = List(user=request.user,name=key_name,pretty_name=pretty_name)
                watch_list.save()
                response_text["filter"] = {
                    "name":key_name,
                    "pretty_name":pretty_name,
                    "type":"custom"
                }
                response_text["error"] = False

        response_text["error_messages"] = form.errors
    return HttpResponse(json.dumps(response_text), content_type='application/json')

@login_required
@transaction.atomic
def search(request):
    movies = []
    tv_series = []
    people = []
    lists = List.objects.filter(user=request.user)

    context = {
        "movies" : movies,
        "tv_series" : tv_series,
        "people" : people,
        "lists" : lists,
        "list_form" : AddListForm()
    }

    if request.method != "GET" or "query" not in request.GET:
        return render(request, "search.html", context)

    query = request.GET["query"]

    # Check if the value is in the cache
    content_types = "movie,show,person"
    url = 'https://api-v2launch.trakt.tv/search?query={0}&type={1}&limit=50'.format(query, content_types)
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version' : '2',
        'trakt-api-key' : client_id
    }

    tag = "search-{0}".format(query.strip().lower())
    cached = SEARCH_CACHE.get(tag)
    if cached:
        # Found in the cache
        result = json.loads(cached)
    else:
        result = requests.get(url, headers=headers)
        SEARCH_CACHE.set(tag, result.text, CACHE_TIMEOUT)
        result = result.json()

    lists = List.objects.filter(user=request.user)

    for element in result:
        if element["type"] == "person":
            element["person"]["score"] = element["score"]
            element["person"]["type"] = element["type"]
            people.append(element["person"])
        elif element["type"] == "movie":
            element["movie"]["score"] = element["score"]
            element["movie"]["type"] = element["type"]
            element["movie"]["owns"] = Movie.objects.filter(trakt_id=element["movie"]["ids"]["trakt"],list__in=lists).exists()
            movies.append(element["movie"])
        elif element["type"] == "show":
            element["show"]["score"] = element["score"]
            element["show"]["type"] = element["type"]
            element["show"]["owns"] = UserTVShow.objects.filter(user=request.user,trakt_id=element["show"]["ids"]["trakt"],list__in=lists).exists()
            tv_series.append(element["show"])

    split_relevant(query, people)
    split_relevant(query, movies)
    split_relevant(query, tv_series)

    movies.sort(cmp=lambda x,y: compare_results(query,x,y))
    tv_series.sort(cmp=lambda x,y: compare_results(query,x,y))

    context["movies"] = movies
    context["tv_series"] = tv_series

    return render(request, 'search.html', context)

@login_required
def movies(request):
    if request.method != "GET":
        return HttpResponseRedirect(reverse("login"))

    lists = List.objects.filter(user=request.user).exclude(name="watching")
    movies = Movie.objects.filter(list__in=lists).distinct()
    context = {
        'content':'movies',
        'media': movies,
        'lists' : lists,
        "list_form" : AddListForm(),
        "settings_form" : SettingsForm(user=request.user)
    }
    return render(request, 'movies.html', context)

@login_required
def shows(request):
    if request.method != "GET":
        return HttpResponseRedirect(reverse("login"))

    lists = List.objects.filter(user=request.user)
    user_shows = UserTVShow.objects.filter(list__in=lists).distinct()
    shows = []
    for show in user_shows:
        setattr(show.show, "list_set", show.list_set)
        shows.append(show.show)

    context = {
        'content':'shows',
        'media': shows,
        'lists' : lists,
        "list_form" : AddListForm()
    }
    return render(request, 'shows.html', context)