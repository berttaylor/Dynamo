from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from users.forms import SignUpForm
from users.models import User


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


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    """
    Allows users to update their details
    """

    template_name = "app/home/user_details.html"
    model = User
    fields = (
        "first_name",
        "last_name",
        "email"
    )

    def get_object(self, queryset=None):
        return self.request.user
