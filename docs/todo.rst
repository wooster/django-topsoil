* BaseResource uses an ugly hack to set self.__name__ so the cache_page
  decorator will work.
  - Need to come up with a better solution for caching.
  - What can we do to work better with the Django view decorators?
* ratelimit_post and login_requred decorator equivalents
