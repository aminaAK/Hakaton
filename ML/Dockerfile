# pull official base image
FROM python:3.12.7

# set work directory
WORKDIR /usr/src/ML

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# # install system dependencies
RUN pip install netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# # copy entrypoint.sh
# COPY ./entrypoint.sh .
# RUN sed -i 's/\r$//g' /usr/src/ML/entrypoint.sh
# RUN chmod +x /usr/src/ML/entrypoint.sh

# copy project
COPY . .

# # run entrypoint.sh
# ENTRYPOINT ["/usr/src", "-x", "/ML/entrypoint.sh"]
