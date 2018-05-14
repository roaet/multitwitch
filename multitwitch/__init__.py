from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from .config import routes
from multitwitch.models import initialize_sql


def db(request):
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()
    request.add_finished_callback(cleanup)

    return session

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    print(settings)
    print(global_config)
    config = Configurator(settings=settings)
    config.scan('multitwitch.models')
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    initialize_sql(engine)
    config.registry.dbmaker = sessionmaker(bind=engine)
    config.add_request_method(db,reify=True)

    config.include(routes)
    return config.make_wsgi_app()

