from flask import Flask
import psycopg2
import views
import initdb

app = Flask(__name__)
app.config.from_object("settings")
app.add_url_rule("/", view_func=views.home_page)
app.add_url_rule("/classes", view_func=views.classes_page, methods=["GET", "POST"])
app.add_url_rule("/add/class", view_func=views.class_addition_page, methods=["GET", "POST"])
app.add_url_rule("/add/course", view_func=views.course_addition_page, methods=["GET", "POST"])
app.add_url_rule("/add/instructor", view_func=views.instructor_addition_page, methods=["GET", "POST"])
app.add_url_rule("/add/courseworktype", view_func=views.courseworktype_addition_page, methods=["GET", "POST"])
app.add_url_rule("/course/<string:courseCode>", view_func=views.course_page, methods=["GET", "POST"])
app.add_url_rule("/course/<string:courseCode>/edit", view_func=views.course_edit_page, methods=["GET", "POST"])
app.add_url_rule("/class/<int:semester>/<int:crn>", view_func=views.class_page, methods=["GET", "POST"])
app.add_url_rule("/class/<int:semester>/<int:crn>/edit", view_func=views.class_edit_page, methods=["GET", "POST"])
app.add_url_rule("/class/<int:semester>/<int:crn>/addwork", view_func=views.coursework_addition_page, methods=["GET", "POST"])
app.add_url_rule("/class/<int:semester>/<int:crn>/syllabus", view_func=views.syllabus_page)
app.add_url_rule("/class/<int:semester>/<int:crn>/delete", view_func=views.class_delete_redirector)
app.add_url_rule("/work/<int:workID>/", view_func=views.coursework_page, methods=["GET", "POST"])
app.add_url_rule("/work/<int:workID>/edit", view_func=views.coursework_edit_page, methods=["GET", "POST"])
app.add_url_rule("/class/<int:semester>/<int:crn>/<string:follows>", view_func=views.add_follow_redirector)
app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
app.add_url_rule("/signup", view_func=views.signup_page, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=views.logout_page)
app.add_url_rule("/profile/works", view_func=views.profile_works_page)
app.add_url_rule("/profile/classes", view_func=views.profile_follows_page, methods=["GET", "POST"])

if __name__ == "__main__":
    initdb.initialize()
    getport = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=getport)
