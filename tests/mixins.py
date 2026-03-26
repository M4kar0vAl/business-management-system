from app.main import app


class GetUrlMixin:
    url_name: str

    def get_url(self, **kwargs):
        return app.url_path_for(self.url_name, **kwargs)
