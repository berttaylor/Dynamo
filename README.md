# collabl.io

## Summary

Collabl is a fully functional  **Collaborative Goal Tracking** & **Task Management** web application, written with the following goals in mind:

* Allow individuals users with a similar cause to form online groups
* Allow these groups to plan and track collaborations in a way which is fully featured (see the feature spec below), but also intuitive and simple to use.

To do this, we prioritise the following points when making decisions about the application:

* Simplicity over complexity
* Convenience for all (Brag-worthy technical skills should never be required in order to use the application)

**Documents**:

* Full Specification/ Feature List : https://docs.google.com/document/d/10w7Cqz6SDbyOHe6ItVXebESuKtB6kFSVh2pXAV6un8M/edit?usp=sharing
* Data Model & Hierarchy : https://drive.google.com/file/d/18L7y34p-JRpzon9RWW7iMVCEI4eciJv9/view?usp=sharing
* Endpoint Schema : https://docs.google.com/spreadsheets/d/1Ib8M2oub7MfTZmSC-i9hmN7KmX-QwJes/edit?usp=sharing&ouid=101532288351105639878&rtpof=true&sd=true

**Demo**:

* YouTube Demo / Rundown: TODO

**Data Naming**:

* Users - Anyone who uses the platform
* Groups - Collections of Users with a common cause or interest e.g. 'Riverdale Parents Group'
* Collaborations - Collaborate Tasks or goals which the Group wishes to reach e.g. 'Turn the old school yard into a safe space for teenagers'
* Tasks - The things which much be done to reach the goal, and complete the Collaboration. e.g. 'Paint the walls of the football hut blue' 
* Milestones - Moments where significant progress is made towards the end goal. e.g "Stage One Preparations Complete"

## Technology stack


### Back End

The platform is built on the following technology:

* Python / Django
* PostgreSQL
* Docker

The PostgreSQL database system and the Python/Django code are containerised using Docker, for ease and consistency of deployment.

### Front End - HTMX

The app makes heavy use of HTMX to add async and SPA elements to the interface. Most operations are performed without a full page refresh, with these reserved for more substantial events - e.g. entering the dashboard, deleting a group/collaboration.

The aesthetics are is based on a css theme, and adapted to fulfil all items of functionality described in the specification.

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

(_Important: You will need to complete a local .env file with the correct information. More information will be provided on this in later versions of the app/readme._)

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
  `docker ps` - you should have all the required containers running.
- At `http://127.0.0.1:8000/control`, you should see the admin login page.

## Usage & Testing

(_Demo Data/Fixtures are being created. More information will be provided on this in later versions of the app/readme._)

