from flask import jsonify, g, request
from flask.views import MethodView

from sqlalchemy import select

from app.api.models import session, Todo, TodoList
from app.api.utils import token_required


class TodoAPI(MethodView):

    decorators = (token_required,)

    def get(self):
        stmt = select(Todo).where(Todo.status != "ARCHIVE", Todo.user_id == g.user.id)
        results = session.scalars(stmt).all()

        data = []
        for item in results:
            data.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "status": item.status,
                }
            )

        return jsonify(data)

    def post(self):
        results = request.get_json()

        name = results["name"]
        description = results["description"]

        if not name:
            return jsonify("name is required."), 400

        todo = Todo(name=name, description=description, user_id=g.user.id)

        results = session.add(todo)
        session.commit()

        return jsonify(
            {
                "id": todo.id,
                "name": todo.name,
                "description": todo.description,
                "status": todo.status,
            }
        )


class TodoDetailAPI(MethodView):

    decorators = (token_required,)

    def _get_item(self, id):
        stmt = select(Todo).where(Todo.id == id, Todo.user_id == g.user.id)
        item = session.execute(stmt).scalar_one_or_none()

        if item is None:
            return jsonify({"message": "Todo Not Found!"}), 404

        return item

    def get(self, id):
        todo = self._get_item(id)

        todo_list = []
        for item in todo.list_collection:
            todo_list.append({"id": item.id, "name": item.name, "status": item.status})

        return jsonify(
            {
                "id": todo.id,
                "name": todo.name,
                "description": todo.description,
                "status": todo.status,
                "todo_list": todo_list,
            }
        )

    def patch(self, id):
        todo = self._get_item(id)

        results = request.get_json()

        name = results["name"]
        description = results["description"]

        if not name:
            return jsonify("name is required."), 400

        todo.name = name
        todo.description = description

        session.commit()

        todo_list = []
        for item in todo.list_collection:
            todo_list.append({"id": item.id, "name": item.name, "status": item.status})

        return jsonify(
            {
                "id": todo.id,
                "name": todo.name,
                "description": todo.description,
                "status": todo.status,
                "todo_list": todo_list,
            }
        )

    def delete(self, id):
        todo = self._get_item(id)

        session.delete(todo)
        session.commit()

        return "", 204


class TodoArchiveListAPI(MethodView):

    decorators = (token_required,)

    def get(self):
        stmt = select(Todo).where(Todo.status == "ARCHIVE", Todo.user_id == g.user.id)
        results = session.scalars(stmt).all()

        data = []
        for item in results:
            data.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "status": item.status,
                }
            )

        return jsonify(data)


class TodoArchiveAPI(MethodView):

    decorators = (token_required,)

    def _get_item(self, id):
        stmt = select(Todo).where(Todo.id == id, Todo.user_id == g.user.id)
        item = session.execute(stmt).scalar_one_or_none()

        if item is None:
            return jsonify({"message": "Todo Not Found!"}), 404

        return item

    def patch(self, id):
        todo = self._get_item(id)

        if todo.status == "COMPLETE" or check_complete(todo):
            todo.status = "ARCHIVE"

            session.commit()

            return jsonify({"message": f"'{todo.name}' List Archived."})

        return jsonify({"message": f"Error: '{todo.id}' List is not Completed."})


class TodoListAPI(MethodView):

    decorators = (token_required,)

    def _get_item(self, id):
        stmt = select(Todo).where(Todo.id == id, Todo.user_id == g.user.id)
        item = session.execute(stmt).scalar_one_or_none()

        if item is None:
            return jsonify({"message": "Todo Not Found!"}), 404

        return item

    def get(self, id):
        todo = self._get_item(id)

        todo_list = []
        for item in todo.list_collection:
            todo_list.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "status": item.status,
                    "todo_id": item.todo_id,
                }
            )

        return jsonify(todo_list)

    def post(self, id):
        todo = self._get_item(id)
        results = request.get_json()

        name = results["name"]

        if not name:
            return jsonify("name is required."), 400

        todo_item = TodoList(name=name, todo_id=todo.id)

        session.add(todo_item)

        if todo.status == "COMPLETE":
            todo.status = "ACTIVE"

        session.commit()

        return jsonify(
            {
                "id": todo_item.id,
                "name": todo_item.name,
                "status": todo_item.status,
                "todo_id": todo_item.todo_id,
            }
        )


class TodoListDetailAPI(MethodView):

    decorators = (token_required,)

    def _get_item(self, id, list_id):
        stmt = select(TodoList).where(TodoList.id == list_id, TodoList.todo_id == id)
        item = session.execute(stmt).scalar_one_or_none()

        if item:
            if item.todo.user_id == g.user.id:
                return item

        return jsonify({"message": "Todo Item Not Found!"}), 404

    def get(self, id, list_id):
        todo_item = self._get_item(id, list_id)
        return jsonify(
            {
                "id": todo_item.id,
                "name": todo_item.name,
                "status": todo_item.status,
                "todo": {
                    "name": todo_item.todo.name,
                    "id": todo_item.todo.id,
                    "status": todo_item.todo.status,
                    "description": todo_item.todo.description,
                },
            }
        )

    def patch(self, id, list_id):
        todo_item = self._get_item(id, list_id)

        results = request.get_json()

        name = results["name"]

        if not name:
            return jsonify("name is required."), 400

        todo_item.name = name
        session.commit()

        return jsonify(
            {
                "id": todo_item.id,
                "name": todo_item.name,
                "status": todo_item.status,
                "todo": {
                    "name": todo_item.todo.name,
                    "id": todo_item.todo.id,
                    "status": todo_item.todo.status,
                    "description": todo_item.todo.description,
                },
            }
        )

    def delete(self, id, list_id):
        todo_item = self._get_item(id, list_id)

        session.delete(todo_item)

        if todo_item.todo != "COMPLETE":
            if check_complete(todo_item.todo):
                todo_item.todo.status = "COMPLETE"

        session.commit()

        return "", 204


class TodoListCheckAPI(MethodView):

    decorators = (token_required,)

    def _get_item(self, id, list_id):
        stmt = select(TodoList).where(TodoList.id == list_id, TodoList.todo_id == id)
        item = session.execute(stmt).scalar_one_or_none()

        if item:
            if item.todo.user_id == g.user.id:
                return item

        return jsonify({"message": "Todo Item Not Found!"}), 404

    def patch(self, id, list_id):
        todo_item = self._get_item(id, list_id)

        todo_item.status = "COMPLETE"

        if check_complete(todo_item.todo):
            todo_item.todo.status = "COMPLETE"

        session.commit()

        return jsonify({"message": f"Item '{todo_item.name}' Checked!"})


def check_complete(todo):

    if len(todo.list_collection) > 0:
        for item in todo.list_collection:
            if item.status == "NOT_DONE":
                return False

        return True

    return False
