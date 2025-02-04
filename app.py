from flask_apscheduler import APScheduler
from app import create_app
from app.utils.scripts import check_health

app = create_app()
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Add scheduled job
@scheduler.task('interval', id='health_check', minutes=7.5, misfire_grace_time=900)
def scheduled_health_check():
    print("Scheduled health check")
    check_health()

if __name__ == "__main__":
    app.run(debug=True)