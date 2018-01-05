from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserInfo(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

class Movie(models.Model):
  trakt_id     = models.IntegerField(primary_key=True)
  title        = models.CharField(max_length=30)
  released     = models.DateField(null=True)
  poster_url   = models.URLField(blank=True, null=True)
  fanart_url   = models.URLField(blank=True, null=True)
  runtime      = models.IntegerField()
  certification = models.CharField(max_length=10, default="NR")
  overview     = models.CharField(max_length=200, blank=True, null=True)

  def __unicode__(self):
    return str(self.trakt_id)

class Genre(models.Model):
  movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
  genre = models.CharField(max_length=30)

  def __unicode__(self):
    return str(self.genre)

class TVShow(models.Model):
  trakt_id     = models.IntegerField(primary_key=True)
  title        = models.CharField(max_length=30)
  first_aired  = models.DateField(null=True)
  poster_url   = models.URLField(blank=True, null=True)
  fanart_url   = models.URLField(blank=True, null=True)
  overview     = models.CharField(max_length=200, blank=True, null=True)
  status       = models.CharField(max_length=30, null=True)
  airs         = models.DateField(null=True)
  network      = models.CharField(max_length=30, null=True)
  certification = models.CharField(max_length=10, null=True, default="NR")

class ShowGenre(models.Model):
  show  = models.ForeignKey(TVShow, on_delete=models.CASCADE)
  genre = models.CharField(max_length=30)

  def __unicode__(self):
    return str(self.genre)

class UserTVShow(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  trakt_id = models.IntegerField(primary_key=True)
  watched = models.BooleanField(default=False)
  show = models.ForeignKey(TVShow, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'trakt_id')

class List(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  movies = models.ManyToManyField(Movie)
  name = models.CharField(max_length=30)
  pretty_name = models.CharField(max_length=30)
  type = models.CharField(max_length=30, default="custom")
  tv_shows = models.ManyToManyField(UserTVShow)

  def __unicode__(self):
    return self.pretty_name

  class Meta:
    unique_together = ('user', 'name')

class TVSeason(models.Model):
  trakt_id      = models.IntegerField(primary_key=True)
  season_number = models.IntegerField()
  show          = models.ForeignKey(TVShow)
  poster_url    = models.URLField(blank=True, null=True)
  thumb_url     = models.URLField(blank=True, null=True)
  overview      = models.CharField(max_length=200, blank=True, null=True)

class Episode(models.Model):
  trakt_id       = models.IntegerField(primary_key=True)
  episode_number = models.IntegerField(null=True)
  title          = models.CharField(max_length=30, null=True)
  season         = models.ForeignKey(TVSeason)
  screenshot_url = models.URLField(blank=True, null=True)
  first_aired  = models.DateField(null=True)
  overview       = models.CharField(max_length=200, blank=True, null=True)

class Settings(models.Model):
  user                  = models.OneToOneField(User, on_delete=models.CASCADE)
  movie_view_mode       = models.CharField(max_length=30, default="poster")
  show_view_mode        = models.CharField(max_length=30, default="fanart")
  search_view_mode      = models.CharField(max_length=30, default="poster")
  movie_default_filter  = models.CharField(max_length=30, default="to-watch")
  show_default_filter   = models.CharField(max_length=30, default="watching")
  search_default_filter = models.CharField(max_length=30, default="all")
  movie_sort_style      = models.CharField(max_length=30, default="release_date")
  show_sort_style       = models.CharField(max_length=30, default="latest_episode")
  search_sort_style     = models.CharField(max_length=30, default="relevancy")
  movie_alert_period    = models.CharField(max_length=30, default="day_before")
  show_alert_period     = models.CharField(max_length=30, default="15_before")
  email_notification    = models.CharField(max_length=10, default="true")
  home_page             = models.CharField(max_length=30, default="movies")

class UserTVSeason(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  trakt_id = models.IntegerField(primary_key=True)
  watched = models.BooleanField(default=False)
  season = models.ForeignKey(TVSeason, on_delete=models.CASCADE)
  show = models.ForeignKey(UserTVShow, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'trakt_id')

class UserEpisode(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  trakt_id = models.IntegerField(primary_key=True)
  watched = models.BooleanField(default=False)
  episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
  season = models.ForeignKey(UserTVSeason, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'trakt_id')