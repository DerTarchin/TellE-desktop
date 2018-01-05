from telle.models import *

def get_user_info(user, create=False):
  try:
    user_info = UserInfo.objects.get(user=user)
  except UserInfo.DoesNotExist:
    user_info = None

    if create:
      user_info = UserInfo(user=user)
      user_info.save()

  return user_info

def get_user(username):
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    user = None

  return user

def get_list(user, name):
  try:
    result = List.objects.get(user=user,name=name)
  except List.DoesNotExist:
    result = None

  return result

def get_movie_or_show(user, trakt_id):
  try:
    media = Movie.objects.get(trakt_id=trakt_id)
    media_type = "movie"
  except Movie.DoesNotExist:
    try:
      media = UserTVShow.objects.get(user=user, trakt_id=trakt_id)
      media_type = "show"
    except UserTVShow.DoesNotExist:
      media = None
      media_type = None

  return media, media_type

def get_from_list(list_model, trakt_id, media_type):
  to_search = None
  if media_type == "movie":
    to_search = list_model.movies
    error = Movie.DoesNotExist
  else:
    to_search = list_model.tv_shows
    error = UserTVShow.DoesNotExist

  try:
    print to_search
    print to_search.all()
    result = to_search.all().get(trakt_id=trakt_id)
  except:
    result = None

  return result

