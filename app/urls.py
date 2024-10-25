from django.urls import path
from . import views

urlpatterns = [
    path("login_user/", views.login_user, name="login"),
    path("logout_user/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    path("flux/", views.flux, name="flux"),
    path("subscription/", views.subscription, name="subscription"),
    path("create_ticket/", views.create_ticket, name="create_ticket"),
    path("create_critique/<int:ticket_id>/", views.create_critique, name="create_critique"),
    path("create_ticket_critique/", views.create_ticket_critique, name="create_ticket_critique"),
    path("my_posts/", views.my_posts, name="my_posts"),
    path("modify_ticket/<int:ticket_id>/", views.modify_ticket, name="modify_ticket"),
    path("modify_critique/<int:critique_id>/", views.modify_critique, name="modify_critique"),
]

# TODO ReadmeReadme
# TODO ajouter des tickets / critique

