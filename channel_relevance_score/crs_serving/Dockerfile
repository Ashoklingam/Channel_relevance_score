# Use an official Python runtime as a parent image
FROM python:3.8-slim

# make sure all python dependencies works well
RUN apt-get update && \
    apt-get --assume-yes install wget && \
    rm -rf /var/lib/apt/lists/*

# Add a new user
RUN groupadd -g 61000 docker && useradd -g 61000 -l -M -s /bin/false -u 61000 docker

# Set the working directory to /app
WORKDIR /app

# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
ADD ./crs_serving/requirements.txt /app/requirements.txt

RUN python -m venv venv

# Setting these environment variables are the same as running
# source /env/bin/activate.
ENV VIRTUAL_ENV /venv
ENV PATH /venv/bin:$PATH

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the api code
COPY /crs_serving/ /app

# Sets up the entry point to invoke the server.
CMD [ "python", "channel_relevance_score.py"]