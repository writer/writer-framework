# Deploy with Docker

You can use Docker to deploy Writer anywhere. If you're an experienced Docker user, you may want to go straight to the provided Dockerfile.

## Creating a Docker image

### Setting up

- Make sure you have Docker installed.
- Open a terminal and navigate to your app's folder.
- If your project is not already set up, run `writer create <path>` to initialize your project. This command sets up all necessary files, such as `pyproject.toml`, `main.py`, and `ui.json`, and uses Poetry for dependency management.

### Why Poetry is Used in Writer Framework

Poetry ensures consistent, reproducible environments, simplifies dependency management, and aligns with the Writer Framework’s needs, making it an ideal tool for Docker deployments.

### Creating a Dockerfile

A Dockerfile contains instructions for building a Docker image. Save the following Dockerfile in your app's folder:

```docker
# Use an official Python runtime as a parent image
FROM python:3.10-bullseye

# Update the package repository and install required dependencies
RUN apt-get update -y && mkdir /app
RUN apt-get install build-essential cmake python3-dev -y

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Poetry
RUN pip3 install poetry

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies specified in pyproject.toml
RUN poetry install --only main

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run Writer when the container launches
ENTRYPOINT [ "writer", "run" ]
CMD [ ".",  "--port", "8080", "--host", "0.0.0.0" ]
```

### Building the Docker image

To build the image, run the `docker build` command in your terminal:

1. **Navigate to your project directory**:
   ```sh
   cd path/to/your/app
   ```

2. **Build the Docker image**:
   ```sh
   docker build . -t my_framework_app
   ```

### Running the Docker Container

Once the image is built, you can run a container based on that image:

1. **Run the container**:
   ```sh
   docker run -p 8080:8080 my_framework_app
   ```

2. **Access the application**:
   Open your web browser and go to [http://localhost:8080](http://localhost:8080) to see your app running.

### Publishing Your Docker Image

To publish your Docker image to a registry like Docker Hub:

1. **Login to Docker Hub**:
   ```sh
   docker login
   ```

2. **Tag your image**:
   ```sh
   docker tag my_framework_app:latest my_user/my_framework_app:latest
   ```

3. **Push your image to Docker Hub**:
   ```sh
   docker push my_user/my_framework_app:latest
   ```

### Deploying Your Docker Image

We recommend using Google Cloud Run to deploy your Docker image, which offers a generous free tier and SSL out of the box. Follow the Google Cloud Run documentation to deploy your Docker image and make your app available on the web.
