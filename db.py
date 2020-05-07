from datetime import datetime
from pymongo import MongoClient, ReturnDocument
from config import DB_PASS
from bson import ObjectId

# binary options trading database api functions
class BinaryDB:

   def __init__(self):
      self.client = MongoClient("mongodb+srv://dgn_fly:{}@cluster0-a8pky.mongodb.net/test?retryWrites=true&w=majority".format(DB_PASS))
      self.db = self.client.binary

   def create_user(self, tgram_uid, first_name, last_name):
      # create user and a demo account for initial use populated with 10,000 credits
      # leave ngn_balance empty till user makes deposit

      # create db collection user
      self.users = self.db.users

      self.tgram_uid = tgram_uid
      self.first_name = first_name
      self.last_name = last_name
      # self.ngn_balance = ngn_balance

      # check if user exists and return
      result = self.users.find_one({"tgram_uid": self.tgram_uid})
      if result:
         return result

      # insert the following data into the collection user
      self.user_id = self.users.insert_one({
         "tgram_uid": self.tgram_uid,
         "first_name": self.first_name,
         "last_name": self.last_name,
         "join_date": datetime.utcnow(),
         "active_acct": 'demo',
         "account": {
            "demo_balance": 10000,
            "ngn_balance": None
         }
      }).inserted_id

      return self.user_id

   def update_user_ngn_balance(self, tgram_uid, ngn_balance):
      # update the users ngn_balance after confirming 
      self.tgram_uid = tgram_uid
      self.ngn_balance = ngn_balance
      self.users = self.db.users

      result = self.users.find_one_and_update({ "tgram_uid": self.tgram_uid }, {'$set': { "account.ngn_balance": self.ngn_balance }}, return_document=ReturnDocument.AFTER)
      return result

   def switch_acount(self, tgram_uid, account):
      self.tgram_uid = tgram_uid
      self.account = account
      self.users = self.db.users

      result = self.users.find_one_and_update({ "tgram_uid": self.tgram_uid }, {'$set': { "active_acct": self.account }}, return_document=ReturnDocument.AFTER)
      return result

   def deposit(self, tgram_uid, amount):
      self.tgram_uid = tgram_uid
      self.amount = amount

      # create deposit collection
      self.deposits = self.db.deposits
      self.deposit_id = self.deposits.insert_one({
         "tgram_uid": self.tgram_uid,
         "amount": self.amount,
         "status": 'pending'
      }).inserted_id

      return self.deposit_id


# escrow database api functions
class Escrow:

   def __init__(self):
      self.client = MongoClient("mongodb+srv://dgn_fly:{}@cluster0-a8pky.mongodb.net/test?retryWrites=true&w=majority".format(DB_PASS))
      self.db = self.client.escrow

   def create_user(self, tgram_uid, first_name, last_name):
      self.users = self.db.users

      self.tgram_uid = tgram_uid
      self.first_name = first_name
      self.last_name = last_name

      # check if user exists and return
      result = self.users.find_one({"tgram_uid": self.tgram_uid})
      if result:
         return result

      self.user_id = self.users.insert_one({
         "tgram_uid": self.tgram_uid,
         "first_name": self.first_name,
         "last_name": self.last_name,
         "join_date": datetime.utcnow(),
         "sell_offers": 0,
         "buy_offers": 0
      }).inserted_id

      return self.user_id

   def create_offer(self, tgram_uid, offer_type, amount, coin, price, status):
      self.offers = self.db.offers

      self.tgram_uid = tgram_uid
      self.offer_type = offer_type
      self.amount = amount
      self.coin = coin
      self.price = price
      self.status = status

      offer_id = self.offers.insert_one({
         "tgram_uid": self.tgram_uid,
         "offer_type": self.offer_type,
         "amount": self.amount,
         "coin": self.coin,
         "price": self.price,
         "status": self.status,
         "filled_by": None,
         "fill_method": None,
         "fill_status": 'waiting'
      }).inserted_id

      return offer_id

   def get_offers(self, coin, offer_type):
      self.offers = self.db.offers

      self.coin = coin
      self.offer_type = offer_type

      result = self.offers.find({"offer_type": self.offer_type, "coin": self.coin, "status": 'confirmed', "fill_status": 'waiting'})
      return result

   def get_user_offers(self, tgram_uid):
      self.offers = self.db.offers

      self.tgram_uid = tgram_uid

      result = self.offers.find({"tgram_uid": self.tgram_uid})
      return result

   def add_fill_method(self, offer_id, method):
      self.offers = self.db.offers

      self.offer_id = offer_id
      self.method = method

      result = self.offers.find_one_and_update({"_id": self.offer_id}, {'$set': { "fill_method": self.method }}, return_document=ReturnDocument.AFTER)
      return result

   def fill(self, tgram_uid, offer_id, status):
      self.offers = self.db.offers

      self.tgram_uid = tgram_uid
      self.offer_id = ObjectId(offer_id)
      self.status = status

      result = self.offers.find_one_and_update({"_id": self.offer_id}, {'$set': { "fill_status": self.status, "filled_by": self.tgram_uid }}, return_document=ReturnDocument.AFTER)
      print("inside fill db function", result)
      return result



