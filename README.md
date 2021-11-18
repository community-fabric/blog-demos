# Example IP Fabric Python Code

This repository contains example code for communicating to IP Fabric using Python.
Code being referenced is featured on [IP Fabric Blog](https://ipfabric.io/blog/)

## Information
If you would like to learn more about our product please visit us at [IP Fabric](ipfabric.io). 

## API Programmability - Part 1

This blog talked about the basics of communicating to the API using requests.
We also showed how to use the user interface to create an API key and view API documentation.

Blog:      To Be Posted 
Directory: [api-part-1](api-part-1)

## Python Programmablity- Part 2

In this blog we are using the [ipfabric](https://github.com/community-fabric/python-ipfabric)
Python package in the community-fabric GitHub.

Blog:      To Be Posted
Directory: [python-part-2](python-part-2)

## Python Programmablity- Part 3: Webhooks

IP Fabric enables you to send webhooks to other systems.  What if your other system does not
accept webhooks or you are not able to program logic around incoming data?  In this post we will
create our own webhook listener using FastAPI.

Blog:      To Be Posted
Directory: [python-part-3](python-part-3)

Note: This will deploy using HTTP not HTTPS.  If you want to secure your webpage consider 
using Nginx or visit https://fastapi.tiangolo.com/deployment/https/

Note: Heavy background computation processes might need to require celery workers.  As you add 
automations to this base webhook listener it might degrade performance.  Since IP Fabric 
discoveries are usually scheduled once or twice a day this lightweight API should be enough
to handle your needs.  An example celery project: https://github.com/GregaVrbancic/fastapi-celery
