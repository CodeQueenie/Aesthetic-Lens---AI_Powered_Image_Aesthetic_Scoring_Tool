# Deployment Guide for Aesthetic Lens

This guide provides instructions for deploying the Aesthetic Lens application to various cloud platforms.

## Prerequisites

Before deploying, ensure you have:

1. A working local version of the application
2. Git installed on your machine
3. Account credentials for your chosen cloud platform
4. Required CLI tools for your chosen platform

## Local Deployment with Conda

For local deployment, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aesthetic-lens.git
   cd aesthetic-lens
   ```

2. Create and activate a Conda environment:
   ```
   conda env create -f environment.yml
   conda activate aesthetic-lens
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the application at `http://localhost:5000`

## Google Cloud Platform (App Engine) Deployment

Google App Engine provides a fully managed platform that makes it easy to deploy and scale web applications.

### Setup

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

2. Initialize the SDK and authenticate:
   ```
   gcloud init
   gcloud auth login
   ```

3. Create a new project or select an existing one:
   ```
   gcloud projects create [PROJECT_ID] --name="Aesthetic Lens"
   # or
   gcloud config set project [PROJECT_ID]
   ```

### Configuration

1. Create an `app.yaml` file in the root directory:

   ```yaml
   runtime: python39
   entrypoint: gunicorn -b :$PORT app:app

   env_variables:
     FLASK_APP: app.py
     FLASK_ENV: production

   handlers:
   - url: /static
     static_dir: static
   - url: /.*
     script: auto

   instance_class: F2
   ```

2. Add Gunicorn to your `requirements.txt`:
   ```
   gunicorn==20.1.0
   ```

### Deployment

1. Deploy the application:
   ```
   gcloud app deploy
   ```

2. Access your deployed application:
   ```
   gcloud app browse
   ```

## AWS Elastic Beanstalk Deployment

AWS Elastic Beanstalk is an easy-to-use service for deploying and scaling web applications.

### Setup

1. Install the [AWS CLI](https://aws.amazon.com/cli/) and [EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html)

2. Configure AWS credentials:
   ```
   aws configure
   ```

3. Initialize Elastic Beanstalk:
   ```
   eb init -p python-3.9 aesthetic-lens
   ```

### Configuration

1. Create a `Procfile` in the root directory:
   ```
   web: gunicorn app:app
   ```

2. Add Gunicorn to your `requirements.txt`:
   ```
   gunicorn==20.1.0
   ```

### Deployment

1. Create an environment and deploy:
   ```
   eb create aesthetic-lens-env
   ```

2. Access your deployed application:
   ```
   eb open
   ```

## Microsoft Azure App Service Deployment

Azure App Service is a fully managed platform for building, deploying, and scaling web apps.

### Setup

1. Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

2. Log in to Azure:
   ```
   az login
   ```

3. Create a resource group:
   ```
   az group create --name aesthetic-lens-rg --location eastus
   ```

### Configuration

1. Create a `web.config` file in the root directory:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <configuration>
     <appSettings>
       <add key="PYTHONPATH" value="%APPL_PHYSICAL_PATH%" />
       <add key="WSGI_HANDLER" value="app.app" />
       <add key="WSGI_LOG" value="%APPL_PHYSICAL_PATH%\logs\wsgi.log" />
     </appSettings>
     <system.webServer>
       <handlers>
         <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" scriptProcessor="%PYTHON_HOME%\python.exe|%PYTHON_HOME%\Lib\site-packages\wfastcgi.py" resourceType="Unspecified" requireAccess="Script" />
       </handlers>
     </system.webServer>
   </configuration>
   ```

2. Add `wfastcgi` to your `requirements.txt`:
   ```
   wfastcgi==3.0.0
   ```

### Deployment

1. Create an App Service plan:
   ```
   az appservice plan create --name aesthetic-lens-plan --resource-group aesthetic-lens-rg --sku B1 --is-linux
   ```

2. Create a web app:
   ```
   az webapp create --name aesthetic-lens --resource-group aesthetic-lens-rg --plan aesthetic-lens-plan --runtime "PYTHON|3.9"
   ```

3. Deploy the application:
   ```
   az webapp up --name aesthetic-lens --resource-group aesthetic-lens-rg --sku B1 --location eastus
   ```

## Heroku Deployment

Heroku is a platform as a service (PaaS) that enables developers to build, run, and operate applications entirely in the cloud.

### Setup

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. Log in to Heroku:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create aesthetic-lens
   ```

### Configuration

1. Create a `Procfile` in the root directory:
   ```
   web: gunicorn app:app
   ```

2. Add Gunicorn to your `requirements.txt`:
   ```
   gunicorn==20.1.0
   ```

3. Create a `runtime.txt` file:
   ```
   python-3.9.7
   ```

### Deployment

1. Initialize a Git repository (if not already done):
   ```
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Deploy to Heroku:
   ```
   git push heroku master
   ```

3. Open the application:
   ```
   heroku open
   ```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure that the TensorFlow model is correctly packaged with your deployment or accessible via a URL.

2. **Memory Limits**: Cloud platforms often have memory limits. If your application crashes, consider optimizing the model or upgrading your service tier.

3. **File Permissions**: Ensure that your application has write permissions for the uploads directory.

4. **Environment Variables**: Check that all required environment variables are set in your cloud platform's configuration.

### Logging

To view logs for troubleshooting:

- **Google Cloud Platform**: `gcloud app logs tail`
- **AWS Elastic Beanstalk**: `eb logs`
- **Azure App Service**: `az webapp log tail --name aesthetic-lens --resource-group aesthetic-lens-rg`
- **Heroku**: `heroku logs --tail`

## Performance Optimization

For better performance in production:

1. Use a production-ready WSGI server like Gunicorn or uWSGI
2. Implement caching for static assets
3. Consider using a CDN for serving static files
4. Optimize image processing to reduce memory usage
5. Use a managed database service if you add database functionality
