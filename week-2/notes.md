
API Contracts are agreements that define how two systems communicate through an API. They specify request formats, response structures, methods, and rules to make sure reliable and consistent interaction between services.

API contracts clearly describe how requests and responses should be structured, including endpoints, methods, headers, and data formats.
They help API providers and consumers understand expectations clearly, reducing errors and ensuring smooth system integration.


Breaking change: A breaking change is an API change that forces existing users or applications to change their code in order to keep working.

- such as renaming a field, removing an endpoint, or changing a required input.


API versioning (/v1/, /v2/): A way to release a new version of an API when changes are needed, while allowing older clients to keep using the previous version.

Swagger / OpenAPI: A standard way to describe and document an API. In frameworks like FastAPI, it can also provide an interactive page where you can view and test endpoints.

Backward compatibility: Making changes to the API without breaking existing clients that already depend on the current behaviour.
