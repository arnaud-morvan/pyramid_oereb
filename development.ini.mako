###
# app configuration
###

[app:main]
use = egg:pyramid_oereb

pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en

pyramid_oereb.cfg.file = %(here)s/pyramid_oereb.yml
pyramid_oereb.cfg.section = pyramid_oereb

sqlalchemy.url = sqlite:///%(here)s/pyramid_oereb.sqlite

###
# wsgi server configuration
###

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = ${pyramid_oereb_port}

###
# logging configuration
###

[loggers]
keys = root, pyramid_oereb, sqlalchemy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = DEBUG
handlers = console

[logger_pyramid_oereb]
level = DEBUG
handlers =
qualname = pyramid_oereb

[logger_sqlalchemy]
level = DEBUG
handlers =
qualname = sqlalchemy.engine
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s

[pserve]
