# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import os
from flask_graphql import GraphQLView

basedir = os.path.abspath(os.path.dirname(__file__))
# app initialization
app = Flask(__name__)
app.debug = True

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Modules
db = SQLAlchemy(app)


# Models for database
class Cart(db.Model):
    __tablename__ = 'carts'
    uuid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), index=True, unique=True)
    products = db.relationship('Product', backref='cart')

    def __repr__(self):
        return '<Cart %r>' % self.username


class Product(db.Model):
    __tablename__ = 'products'
    uuid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True, unique=True)
    price = db.Column(db.Float)
    inventory = db.Column(db.INT)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.uuid'))

    def __repr__(self):
        return '<Product %r>' % self.title

# Schema Objects

# Querying ProductObject and CartObject for GRAPHQL
class ProductObject(SQLAlchemyObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node, )

class CartObject(SQLAlchemyObjectType):
   class Meta:
       model = Cart
       interfaces = (graphene.relay.Node, )

# CreateCart Mutation in GraphQL
class CreateCart(graphene.Mutation):

    class Arguments:
        username = graphene.String(required=True)

    cart = graphene.Field(lambda: CartObject)

    def mutate(self, info, username):

        cart = Cart(username=username)

        db.session.add(cart)
        db.session.commit()
        return CreateCart(cart=cart)

# UpdateProduct Mutation in GraphQL
class UpdateProduct(graphene.Mutation):

    class Arguments:
        username = graphene.String(required=True)

    product = graphene.Field(lambda: ProductObject)

    def mutate(self, info, username):

        # Look for product before updating it
        product = Product.query.filter_by(title=username).first()

        # if product is found update it, if not commit None (No change)
        if product is not None:

            if product.inventory > 1:

                product.inventory -= 1

        db.session.add(product)
        db.session.commit()
        return UpdateProduct(product)


# ShoppingCarts
# This is an approach to enforce the cart requirement
# The problem with this approach is that there is no synchronization between the local data and the data in the database
# The way it works is there is a live cars dictionary that stores the create carts that are created via a GET method
# carts = {}
# class ShoppingCart:
#     def __init__(self, username):
#         self.cart_id = username
#         self.products = []
# @app.route('/new_cart/<string:cart_id>')
# def create_cart(cart_id):
#     if cart_id in carts:
#         return "Error, duplicate cart"
#     else:
#         carts[cart_id] = ShoppingCart(cart_id)
#         return cart_id




# This is another approach to enforce the cart requirement
# The problem with this approach is the relationship in the database since the database does not store Lists
# class CreateProduct(graphene.Mutation):
#
#     class Arguments:
#         title = graphene.String(required=True)
#         body = graphene.String(required=True)
#
#     product = graphene.Field(lambda: ProductObject)
#
#     def mutate(self, info, title, body):
#         product = Product(title=title, body=body)
#         db.session.add(product)
#         db.session.commit()
#         return CreateProduct(product=product)

# class AddProduct(SQLAlchemyObjectType):
#
#     class Arguments:
#         cart_username = graphene.String(required=True)
#         product_username = graphene.String(required=True)
#
#     new_product = graphene.Field(lambda: ProductObject)
#
#     if cart_username in carts:
#         new_product = Product.query.filter_by(title=product_username).first()
#         if new_product is not None:
#             carts[cart_username].products.append(product_username)
#             db.session.commit()



class Mutation(graphene.ObjectType):
    # create_product = CreateProduct.Field()
    create_cart = CreateCart.Field()
    # add_product = AddProduct.Field()
    update_product = UpdateProduct.Field()

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_products = SQLAlchemyConnectionField(ProductObject)
    all_carts = SQLAlchemyConnectionField(CartObject)

schema = graphene.Schema(query=Query, mutation=Mutation)

# TO-DO
# Routes
# TO-DO
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)

@app.route('/')
def index():
    return '<p> Hello World</p>'
if __name__ == '__main__':
     app.run()
