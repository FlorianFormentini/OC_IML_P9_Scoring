## Local execution
From the project root folder :  
```sh
docker-compose up [-d] [--build]
```
- `-d` - To not display logs
- `--build` - To also build the images. Required only the first time.

API Swagger : http://localhost:8080/docs
Streamlit UI : http://localhost:8501

During development, it is not necessary to rebuild the images after code modifications, just save the modified files and reload the page (UI or API).

## Deployment on Heroku
Heroku does not support `docker-compose.yml` files but it's possible to build applications composed of several docker images using a `heroku.yml` file.

A Heroku dyno is assigned to each image, however in a free plan it is not possible to have two different 'web' dynos and nor to use a 'worker' dyno to deploy the API.  
According to the [documentation](https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime): 
 - Network linking of dynos is not supported.
 - The web process must listen for HTTP traffic on `$PORT`, which is set by Heroku. `EXPOSE` in Dockerfile is not respected. So it's impossible to manually set requests to the backend.

The only solution found was to create 2 heroku applications each using a 'web' image.  
In order to keep only one Github repository the automatic deployment was abandoned to use the deployment from already built images: 

Connection to Heroku:
```sh
# Log in to Heroku
heroku login
# Log in to Container Registry
heroku container:login
```

API deployment:
```sh
# Access backend folder
cd <root_path>/backend
# Create an app
heroku create <app_name>-back
# Build image and push the image to Container Registry
heroku container:push web
# Release the image to the app
heroku container:release web -a <app_name>-back
# open app
heroku open -a <app_name>-back
```

Then, same process for the frontend deployment:
```bash
# Access backend folder
cd <root_path>/frontend
# Create an app
heroku create <app_name>-front
# Build image and push the image to Container Registry
heroku container:push web -a <app_name>-front
# Release the image to the app
heroku container:release web -a <app_name>-front
# open app
heroku open -a <app_name>-back
```

For the frontend to be able to connect to the API, it is necessary to set its url as an environment variable in the frontend application: `BACKEND_PORT`  
In the Heroku dashboard of the frontend application: Settings > "Reveal Config Vars" button