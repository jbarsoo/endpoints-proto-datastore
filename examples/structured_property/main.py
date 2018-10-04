import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import  EndpointsModel         \
                                         , EndpointsAliasProperty
import re
import logging
_logger = logging.getLogger( __name__)


class Interests( EndpointsModel):
    science = ndb.BooleanProperty()
    technology = ndb.BooleanProperty()
    math = ndb.BooleanProperty()
    politics = ndb.BooleanProperty()


_messages = []
def validate_edu( prop, value):
    if not re.match( r'\w+school|\w+college|b[sa]|masters|phd', value):
        _messages.append( 'The value for \'education\' is invalid.')
    return None # changes nothing.
def validate_gender( prop, value):
    if not re.match( 'm|f|mf|lgbtq', value):
        _messages.append( 'The value for \'gender\' is invalid.')
    return None # changes nothing.
class Demographic( EndpointsModel):
    gender = ndb.StringProperty( validator=validate_gender) # was: choices=( 'm', 'f', 'mf', 'lgbtq')
    education = ndb.StringProperty( validator=validate_edu)
    interests = ndb.LocalStructuredProperty( Interests)


class Product( EndpointsModel):
    title = ndb.StringProperty( required=True)
    creation_date = ndb.DateTimeProperty( auto_now_add=True)
    target_demographic = ndb.StructuredProperty( Demographic)

    def SetId( self, value):
        if not isinstance( value, basestring):
          raise TypeError( '\'title\' must be of type String.')
        key = ndb.Key( Product, value)
        self.UpdateFromKey( key)

    @EndpointsAliasProperty( setter=SetId)
    def id( self):
        if self.key is not None:
            return self.key.string_id()

    @EndpointsAliasProperty( repeated=True)
    def messages( self):
        return _messages or [ 'Okay']


@endpoints.api(  name='products'
               , version='v1'
               , description='Products API')
class ProductsAPI( remote.Service):
    _logger.info( 'Entering ProductsAPI')

    @Product.query_method(  path='products'
                          , name='products.list')
    def ProductsList( self, query):
        _logger.info( 'Entering ProductsList.')
        return query
    
    @Product.method(  path='product/create'
                    , http_method='POST'
                    , request_fields=(  'title'
                                      , 'target_demographic')
                    , response_fields=( 'messages', )
                    , name='product.create')
    def ProductCreate( self, product):
        _logger.info( 'Entering ProductCreate')
        product.id = product.title
        product.put()
        return product

application = endpoints.api_server( [ProductsAPI], restricted=False)
