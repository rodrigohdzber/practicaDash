FROM python:3.8


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
# Expose the API Port
EXPOSE 8080
# Run the server
CMD ["python", "app_esios_final.py"]