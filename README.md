# ShopifyDeveloperChallenge

My minimalist server uses GraphQL.

# To initialize server open up a terminal window, clone the repo and write these commands:

cd ShopifyDeveloperChallenge
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install flask flask-graphql flask-migrate flask-sqlalchemy graphene graphene-sqlalchemy

# You should now have all the requirements installed

Run the following script to have some data to test it with and to initialize the database:

python
>>> from app import db, User, Post
>>> db.create_all()
>>> product = Product()
>>> product.title = "orange"
>>> product.inventory = 180
>>> product.price = 123
>>> db.session.add(product)
>>> db.session.commit()

Now run the following

python app.py

you should be able to go to 127.0.0.1:5000/graphql and navigate using graphql's API

to view the available products:

Run:

{
  allProducts{
    edges{
      node{
        title
        inventory
        price
      }
    }
  }
}

To purchase a product:

mutation {
  UpdateProduct(username:<username>){
    product{
      title
      inventory
    }
  }
}
