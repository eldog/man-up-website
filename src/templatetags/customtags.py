from google.appengine.ext import webapp
import urllib, hashlib

register = webapp.template.create_template_register()

# Usage: {% gravatar foo@bar.com %} or {% gravatar foo@bar.com 40 R http://foo.com/bar.jpg %}
def gravatar(email, size = 80, rating = 'g', default_image = ''):
    gravatar_url = "http://www.gravatar.com/avatar/"
    gravatar_url += hashlib.md5(email).hexdigest()
    gravatar_url += urllib.urlencode({'s': str(size), 'r': rating, 'd': default_image})
    return """<img src="%s" alt="gravatar" />""" % gravatar_url
# Possibly: register.filter("gravatar", gravatar)

register.simple_tag(gravatar)
