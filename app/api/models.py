from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


engine = create_engine("sqlite:///instance/flaskr.sqlite")

metadata = MetaData()
metadata.reflect(engine)

Base = automap_base(metadata=metadata)
Base.prepare()

Todo = Base.classes.todo
User = Base.classes.user
TodoList = Base.classes.list

session = Session(engine)
