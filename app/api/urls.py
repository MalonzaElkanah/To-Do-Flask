from app.api.auth import UserRegisterAPI, UserLoginAPI
from app.api.todo import (
    TodoAPI,
    TodoDetailAPI,
    TodoListAPI,
    TodoListDetailAPI,
    TodoListCheckAPI,
    TodoArchiveAPI,
    TodoArchiveListAPI,
)


def api_urls(app):
    app.add_url_rule(
        "/api/auth/register/", view_func=UserRegisterAPI.as_view("user_register")
    )
    app.add_url_rule("/api/auth/login/", view_func=UserLoginAPI.as_view("user_login"))

    app.add_url_rule("/api/todo/", view_func=TodoAPI.as_view("todo"))
    app.add_url_rule(
        "/api/todo/<int:id>/", view_func=TodoDetailAPI.as_view("todo_detail")
    )

    app.add_url_rule(
        "/api/todo/<int:id>/list/", view_func=TodoListAPI.as_view("todo_list")
    )
    app.add_url_rule(
        "/api/todo/<int:id>/list/<int:list_id>/",
        view_func=TodoListDetailAPI.as_view("todo_list_detail"),
    )
    app.add_url_rule(
        "/api/todo/<int:id>/list/<int:list_id>/check/",
        view_func=TodoListCheckAPI.as_view("todo_list_check"),
    )

    app.add_url_rule(
        "/api/todo/archives/", view_func=TodoArchiveListAPI.as_view("todo_archive_list")
    )
    app.add_url_rule(
        "/api/todo/<int:id>/archive/", view_func=TodoArchiveAPI.as_view("todo_archive")
    )
