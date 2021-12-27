from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from users.forms import SignUpForm


def SignUpView(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(
                username=username, password=raw_password, request=request
            )
            login(request, user)
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "static_site/registration/signup.html", {"form": form})
