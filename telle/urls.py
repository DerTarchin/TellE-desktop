from django.conf.urls import include, url
from telle import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^register$', views.register, name='register'),
    url(r'^search$', views.search, name='search'),
    url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^movies$', views.movies, name='movies'),
    url(r'^shows$', views.shows, name='shows'),
    url(r'^add_list$', views.add_list, name='add_list'),
    url(r'^delete_list$', views.delete_list, name='delete_list'),
    url(r'^manage_list$', views.manage_list, name='manage_list'),
    url(r'^add_media$', views.add_media, name='add_media'),
    url(r'^remove_media$', views.remove_media, name='remove_media'),
    url(r'^delete_account$', views.delete_account, name='delete_account'),
    url(r'^update_settings$', views.update_settings, name='update_settings'),
    url(r'^movies/(?P<trakt_id>[^/]+)$', views.movie_info_page, name='movie_info_page'),
    url(r'^shows/(?P<trakt_id>[^/]+)$', views.show_info_page, name='show_info_page'),
    url(r'^people/(?P<trakt_id>[^/]+)$', views.person_info_page, name='person_info_page'),
    url(r'^manage_season$', views.manage_season, name='manage_season'),
    url(r'^manage_episode$', views.manage_episode, name='manage_episode'),
    url(r'^admin$', views.admin, name='admin'),
    url(r'^clear_cache$', views.clear_cache, name='clear_cache'),
]