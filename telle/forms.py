from django import forms

from django.contrib.auth.models import User
from .models import *

import re
alphanumeric = re.compile("^[0-9a-zA-Z\s]*$")

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "email"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(UserForm, self).__init__(*args, **kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if first_name.strip() == "":
            first_name = ""

        return first_name

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # if self.user.username != email and User.objects.filter(username=email).exists():
        #     print email
        #     raise forms.ValidationError("User already exists with that email.")

        # TODO: User actual email
        return self.user.username

class SettingsForm(forms.ModelForm):

    class Meta:
        model = Settings
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(SettingsForm, self).__init__(*args, **kwargs)


    def clean_movie_view_mode(self):
        movie_view_mode = self.cleaned_data.get("movie_view_mode")

        if movie_view_mode not in ["poster", "fanart"]:
            raise forms.ValidationError("Invalid movie view mode.")

        return movie_view_mode

    def clean_show_view_mode(self):
        show_view_mode = self.cleaned_data.get("show_view_mode")

        if show_view_mode not in ["poster", "fanart"]:
            raise forms.ValidationError("Invalid show view mode.")

        return show_view_mode

    def clean_search_view_mode(self):
        search_view_mode = self.cleaned_data.get("search_view_mode")

        if search_view_mode not in ["poster", "fanart"]:
            raise forms.ValidationError("Invalid search view mode.")

        return search_view_mode

    def clean_movie_sort_style(self):
        movie_sort_style = self.cleaned_data.get("movie_sort_style")

        if movie_sort_style not in ["date_added", "release_date", "alphabetical"]:
            raise forms.ValidationError("Invalid movie sort style.")

        return movie_sort_style

    def clean_show_sort_style(self):
        show_sort_style = self.cleaned_data.get("show_sort_style")

        if show_sort_style not in ["date_added", "latest_episode", "alphabetical"]:
            raise forms.ValidationError("Invalid show sort style.")

        return show_sort_style

    def clean_search_sort_style(self):
        search_sort_style = self.cleaned_data.get("search_sort_style")

        if search_sort_style not in ["release_date", "relevancy", "alphabetical"]:
            raise forms.ValidationError("Invalid search sort style.")

        return search_sort_style

    def clean_movie_default_filter(self):
        movie_default_filter = self.cleaned_data.get("movie_default_filter")

        if (movie_default_filter == "watching") or not (movie_default_filter == "all" or List.objects.filter(user=self.user, name=movie_default_filter).exists()):
            raise forms.ValidationError("Invalid movie default filter.")

        return movie_default_filter

    def clean_show_default_filter(self):
        show_default_filter = self.cleaned_data.get("show_default_filter")

        if not (show_default_filter == "all" or List.objects.filter(user=self.user, name=show_default_filter).exists()):
            raise forms.ValidationError("Invalid show default filter.")

        return show_default_filter

    def clean_search_default_filter(self):
        search_default_filter = self.cleaned_data.get("search_default_filter")

        if search_default_filter not in ["all", "movies", "shows", "people"]:
            raise forms.ValidationError("Invalid search default filter.")

        return search_default_filter

    def clean_movie_alert_period(self):
        movie_alert_period = self.cleaned_data.get("movie_alert_period")

        if movie_alert_period not in ["week_before", "day_before", "day_of", "day_after", "week_after"]:
            raise forms.ValidationError("Invalid movie alert period.")

        return movie_alert_period

    def clean_show_alert_period(self):
        show_alert_period = self.cleaned_data.get("show_alert_period")

        if show_alert_period not in ["week_before", "day_before", "hour_before", "15_before", "15_after", "hour_after", "day_after", "week_after"]:
            raise forms.ValidationError("Invalid show alert period.")

        return show_alert_period

    def clean_email_notification(self):
        email_notification = self.cleaned_data.get("email_notification")

        if email_notification not in ["true", "false"]:
            raise forms.ValidationError("Invalid email notification choice.")

        return email_notification

    def clean_home_page(self):
        home_page = self.cleaned_data.get("home_page")

        if home_page not in ["movies", "shows"]:
            raise forms.ValidationError("Invalid home page.")

        return home_page

class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", "first_name", "password"]
        widgets = {
            "first_name" : forms.TextInput(attrs={"placeholder": "nickname"}),
            "email" : forms.TextInput(attrs={"placeholder": "email"}),
            "password" : forms.PasswordInput(attrs={"placeholder": "password"})
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if first_name.strip() == "":
            first_name = ""

        return first_name

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("User already exists with that email.")

        return email

class SearchForm(forms.Form):
    pass

class DeleteListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name"]

class AddListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["pretty_name"]
        widgets = {
            "pretty_name": forms.TextInput(attrs={"autocomplete" : "off",
                                                  "placeholder" : "Add new list"})
        }

    def clean_pretty_name(self):
        pretty_name = self.cleaned_data.get("pretty_name").strip()

        # TODO: Check max size condition

        if not pretty_name:
            raise forms.ValidationError("Cannot have empty list name")
        elif pretty_name.lower() == "all":
            raise forms.ValidationError("All is not a valid list name")
        elif not alphanumeric.match(pretty_name):
            raise forms.ValidationError("Name must be alphanumeric")

        return pretty_name

class ManageListForm(forms.Form):
    trakt_id  = forms.IntegerField(required=True,
                                   error_messages={"required": "trakt_id is required"})
    name      = forms.CharField(required=True,
                                error_messages={"required": "List name is required"})

    def clean_trakt_id(self):
        trakt_id = self.cleaned_data.get("trakt_id")

        if trakt_id < 0:
            raise forms.ValidationError("trakt_id must be a positive integer")

        return trakt_id