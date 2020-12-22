from flask import Flask
import psycopg2
import views

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/classes", view_func=views.classes_page, methods=["GET", "POST"])
    app.add_url_rule("/class/<int:semester>/<int:crn>", view_func=views.class_page)
    return app

if __name__ == "__main__":
    app = create_app()
    getport = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=getport)