from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from users.forms import SignUpForm


def sign_up_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(
                email=email, password=raw_password, request=request
            )
            login(request, user)
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "landing/registration/signup.html", {"form": form})
