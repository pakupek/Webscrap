# Use python image
FROM python:3.12
 
# Set the working directory inside the container
WORKDIR /webscrap
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
RUN apt-get update && apt-get install -y libpq-dev && apt-get clean

COPY requirements.txt .


# Install dependencies
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt


COPY entrypoint.sh ./

RUN chmod +x ./entrypoint.sh

COPY . .

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]