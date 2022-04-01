## Deployment on Heroku
In order to push several images the [heroku documentation](https://devcenter.heroku.com/articles/container-registry-and-runtime) states that each image's Dockerfile should be in its image folder and not in the root of the project and that they must be renamed `Dockerfile.<process-type>`.
```
├── backend
│   ├── ...
|   └── Dockerfile.back
├── frontend
|   ├── ...
|   └── Dockerfile.front
└── docker-compose.yml
```

Then, it is possible to fully manage the deployment with the Heroku CLI :
```sh
# Log in to Heroku
heroku login
# Log in to Container Registry
heroku container:login
# Create an app (from projhect root folder)
heroku create <app_name>
```

From the project root folder :
```sh
# Build and push images
heroku container:push --recursive -a <app_name>
# Create a new release
heroku container:release back front -a <app_name>
```