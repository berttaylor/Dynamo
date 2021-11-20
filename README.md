# DynamoAPI

## Summary

DynamoAPI is a fully functional REST-API for **Collaborative Goal Tracking** & **Task Management**

It is written in Python/Django, and using the tools made available by DRF (Django Rest Framework). 

**Features**:

* YouTube Demo / Rundown: TODO

* Full Specification/ Feature List : https://docs.google.com/document/d/1BxU15l53dZzGxrcrWOXJelseyPZ2xzWbcYuOos9DTSg/edit?usp=sharing

**System Overview**:

* Users - Anyone who uses the platform
* Groups - Collections of Users with a common cause or interest e.g. 'Riverdale Parents Group'
* Collaborations - Collaborate Tasks or goals which the Group wishes to reach e.g. 'Turn the old school yard into a safe space for teenagers'
* Tasks - The things which much be done to reach the goal, and complete the Collaboration. e.g. 'Paint the walls of the football hut blue' 
* Milestones - Moments where significant progress is made towards the end goal. e.g "Stage One Preparations Complete"

## Technology stack

The platform is built on the following technology:
* Python / Django
* Django Rest Framework
* PostgreSQL
* Docker

The PostgreSQL database system and the Python/Django code are containerised using Docker, for ease and consistency of deployment.


### Local development environment

The local development environment is designed to mimic a production
environment as far as is possible. 

We use the following local Docker Compose containers:

* db - database container for PostgreSQL
* nginx - reverse proxy container for Nginx
* web - backend container, with both Django + Gunicorn
* redis - message queue for Celery tasks
* worker - container specifically for Celery workers

## Building the application locally

(_Important: You will need to complete the local .env.dev file with the correct information. More information will be provided on this in later versions of the app/readme._)

To get the build running locally, there are a few things that need to happen:

* Clone the repository locally, and get hold of the local `.env.dev` file.
* Build all of the Docker images (which also installs all of the requirements)
  using `make -f make-dev build`.
* This should also create a local version of the production database.
* To migrate the new local db using the local migrations as a base, we
  use `make -f make-dev migrate`.
* Create a super user for local admin access using `make -f make-dev createsuperuser`.

You will now have a built system that you can log into.

__What you should see__

- After the successful build, check that your containers cane run by using `make -f make-dev up`.
  You should have obvious terminal output that confirms this, but you can also run
  `docker ps` - you should have all of the required containers running.
- At `http://127.0.0.1:8000/`, you should see the browsable API (DRF)
- At `http://127.0.0.1:8000/admin`, you should see the admin login page.

## Usage & Testing

The application uses a POSTMAN collection test suite for interacting and further Test Driven Development. 

It provides a useful guide as to:
* how to register/authenticate using JWT
* which endpoints are available 
* what the API expects to receive
* what the API will return

Get access to the Postman collection here - https://www.postman.com/restless-shuttle-820873/workspace/dynamo/overview

NOTE: The tests are chained sequentially, and as such to run all of them, they depend on each other.

### 🎉 Happy Building! 🎉
