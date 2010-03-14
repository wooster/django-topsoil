* OAuth integration.
* Middleware to disable cookie-based auth on API requests and default
  to one of the authenticators defined in a settings file.
* Twitter-style rate limiting.
* Add instance of {"all", "/"} for Resource.
  * Explore integration of resource. Need to pass in 'scope' param in
    OAuth request as an additional parameter.
* Add views for viewing and revoking authorized apps.
