from .api import app

if __name__ == "__main__":
    print("=" * 60)
    print("OpenStack AI Resource Forecasting Service")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)