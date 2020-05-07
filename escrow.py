from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction
from telegram.ext import ConversationHandler
from db import Escrow

# buy conversation states jouurney
OFFER_START, ONE, TWO, THREE = range(4)
END = ConversationHandler.END

# offer start state handler function
def offer(update, context):
   user = update.message.from_user
   chat_id = update.message.chat_id
   bot = context.bot
   bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

   escrow_db = Escrow()
   result = escrow_db.create_user(user.id, user.first_name, user.last_name)
   print(result)

   update.message.reply_text(
      "{}, Welcome to the Oreo Crypt market place where you can place, buy or sell offers for BITCOIN, ETHEREUM and RIPPLE using our shorthand commands, as shown below\n\nSell command goes like this: /sell <amount> <coin> @<price_per_coin>\nE.g: /sell 5.32 btc @3250190\n\nBuy command goes like this: /buy <amount> <coin> @<price_per_coin>\nE.g: /buy 5.32 btc @2950190\n\nTo ensure trust and fair tranactions, assets and payments will be routed through our escrow accounts or cypto currency wallet\n*A cancellation of offer can be requested at anytime, where by assets will be refunded and your offer removed. Small fees apply to each transactions to cover network costs.\n\nSend /help to see the commands that are available and how to use them.".format(user.first_name),
   )

   return OFFER_START

def help(update, context):
   bot = context.bot
   chat_id = None
   if update.callback_query:
      chat_id = update.callback_query.message.chat_id
   else:
      chat_id = update.message.from_user.id

   bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
   # this will reply with a list of commands and their descriptions
   bot.send_message(
      chat_id=chat_id,
      text="Sell command, place sell offer - \n/sell <amount> <coin> @<price_per_coin> \nE.g: /sell 20.32 eth @46540\n\nBuy command, place buy offer - \n/buy <amount> <coin> @<price_per_coin> \nE.g: /buy 4.23 btc @3210920\n\nShow command, to display offers - \n/show <coin> <offer_type> \nE.g; /show btc buy-list or /show btc sell-list\n\nFill command, accept an offer and begin transaction - \n/fill <offer_sn> E.g /fill 6 (the <offer_sn> serial number is from the displayed offer list\n\nNOTE: for support message @fridai2000"
   )
   
   return OFFER_START



# orders
def buy(update, context):
   user = update.message.from_user
   chat_id = update.message.chat_id
   bot = context.bot
   bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

   amount = context.args[0]
   coin = context.args[1]
   price = context.args[2][1:]
   context.user_data['amount'] = amount
   context.user_data['price'] = price
   context.user_data['coin'] = coin

   escrow_db = Escrow()
   result = escrow_db.create_offer(user.id, 'buy', amount, coin, price, 'pending')
   context.user_data['offer_id'] = result
   print(result)

   keyboard = [ [InlineKeyboardButton("CONFIRM", callback_data='confirm-buy')] ]
   markup = InlineKeyboardMarkup(keyboard)

   # add values to context and then to database
   # proceed with clarification, when continued get crypto-address for deposit and send escrow bank payment link
   # close with message that when payment confirmed buy offer will be put up and sent to hundreds of service users

   update.message.reply_text(
      "Please confirm that you're about to place an offer to buy amount: {}, coin: {}, at coin/price of: {} ".format(amount, coin, price),
      reply_markup=markup
   )

   return ONE

def sell(update, context):
   user = update.message.from_user
   bot = context.bot
   chat_id = update.message.chat_id
   bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

   amount = context.args[0]
   coin = context.args[1]
   price = context.args[2][1:]
   context.user_data['amount'] = amount
   context.user_data['price'] = price
   context.user_data['coin'] = coin

   escrow_db = Escrow()
   result = escrow_db.create_offer(user.id, 'sell', amount, coin, price, 'pending')
   context.user_data['offer_id'] = result
   print(result)

   keyboard = [[InlineKeyboardButton("CONFIRM", callback_data='confirm-sell')]]
   markup = InlineKeyboardMarkup(keyboard)

   # add values to context and then to database
   # proceed with clarification, when continued get bank-details for deposit and send escrow-crypto link
   # close with message that when crypto reception confirmed /sell offer will be put up and sent to hundreds of service users

   update.message.reply_text(
      "Please confirm that you're about to place an offer to sell amount: {}, coin: {}, at coin/price of: {} ".format(amount, coin, price),
      reply_markup=markup
   )

   return ONE

def confirm(update, context):
   query = update.callback_query
   chat_id = query.message.chat_id
   bot = context.bot
   bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
   context.user_data['offer'] = query.data

   bot_master_id = 984989153
   bot.send_message(
      chat_id=bot_master_id,
      text="A {} offer of {} {} has been placed, please confirm!".format(context.user_data['offer'][8:], context.user_data['amount'], context.user_data['coin'])
   )

   if query.data == 'confirm-buy':
      bot.edit_message_text(
         chat_id=query.message.chat_id,
         message_id=query.message.message_id,
         text="Your offer is confirmed please proceed as follows:-\n\nReply with your wallet address for the coin in offer\n\nPlease take care not to make a mistake when sending the wallet address for the coin"
      )
   elif query.data == 'confirm-sell':
      bot.edit_message_text(
         chat_id=query.message.chat_id,
         message_id=query.message.message_id,
         text="Your offer is confirmed please proceed as follows:-\n\nReply with your bank account details\n\nPlease take care not to make a mistake when sending the bank account details"
      )
   else:
      bot.edit_message_text(
         chat_id=query.message.chat_id,
         message_id=query.message.message_id,
         text="There was an error with confirming your order please contact support @friday2000 to resolve the issue"
      )

   return TWO

def get_details(update, context):
   text = update.message.text
   bot = context.bot
   chat_id = update.message.chat_id
   bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

   user_id = update.message.from_user.id
   coin = context.user_data['coin']
   offer_id = context.user_data['offer_id']

   wallet_address = None
   if coin == 'btc': wallet_address = '14tDMcXczLa4yWPk3hg2yjT9fmUoJ56KgG'
   if coin == 'eth': wallet_address = '0x09b2063783d357e448f8f33f9b2771ca044d4a3d'
   if coin == 'xrp': wallet_address = 'rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh'

   escrow_db = Escrow()
   res = escrow_db.add_fill_method(offer_id, text)
   print(res)

   # print("User ID: "+str(user_id)+" Chat_id: "+str(chat_id)+" coin: "+coin+", Text: "+text)

   if 'buy' in context.user_data['offer']:
      update.message.reply_text(
         "Alright, your address details are in and saved.\n\nThe next step is super important for trust and security in peer-to-peer trade, which involves our escrow service that will hold your funds until your offer is filled and then will be automatically transfer to the seller upon receipt confirmation from you\n\nNOTE: copy your id: #{} and paste in the required payment gateway field\n\nFollow this link to proceed to make payment to the escrow account: https://paystack.com/pay/oreo-crypt\n\nScreenshot transaction and send to @fridai2000 for confirmation".format(user_id)
      )
   elif 'sell' in context.user_data['offer']:
      update.message.reply_text(
         "Alright, your account details are in and saved.\n\nThe next step is super important for trust and security in peer-to-peer trade, which involves our escrow service that will hold your assets until your offer is filled and then will be automatically transfer to the buyer upon credit confirmation from you\n\nProceed to send the {} into this address below\n\nScreenshot transaction and send to @fridai2000 for confirmation".format(coin.upper())
      )

      bot.send_message(
         chat_id=user_id,
         text=wallet_address
      )
   else:
      update.message.reply_text(
         "Semething went wrong, please try again at some other time"
      )

   return THREE

def show(update, context):
   # e.g /show eth buy-list, /show eth sell
   # add to context.user_data and read list from database
   user = update.message.from_user
   bot = context.bot
   bot.send_chat_action(chat_id=user.id, action=ChatAction.TYPING)

   coin = context.args[0]
   offer_type = context.args[1]

   escrow_db = Escrow()
   offers = escrow_db.get_offers(coin, offer_type)
   print(offers)

   keyboard = [
      [InlineKeyboardButton("CLOSE", callback_data='close')]
   ]
   reply_markup = InlineKeyboardMarkup(keyboard)

   offer_list = "<b>LIST OF {} OFFERS FOR {}</b>\n".format(offer_type, coin)
   if offers.count() == 0:
      update.message.reply_text(
         "There are no {} offers for {}".format(offer_type, coin),
         reply_markup=reply_markup
      )

      return ONE
   for offer in offers:
      offer_list += "\n#{}: <b>{} {} at {}</b>\n".format(offer['_id'], offer['amount'], offer['coin'], offer['price'])


   update.message.reply_text(
      text=offer_list,
      reply_markup=reply_markup,
      parse_mode=ParseMode.HTML
   )

   return ONE



def fill(update, context):
   # fill a particular offer from the list 
   # e.g /fill <offer_id>
   # calculate and make it clear of the amount and transactionary fees involved ([amount] * [price_per_coin])
   # proceed with instrucitons depending on the offer_type
   # create a job queue to check up on both parties of the deal
   bot = context.bot
   user = update.message.from_user
   bot.send_chat_action(chat_id=user.id, action=ChatAction.TYPING)

   offer_id = context.args[0][1:]
   print(offer_id)
   escrow_db = Escrow()
   res = escrow_db.fill(user.id, offer_id, 'pending')
   print(res)

   total = (float(res['amount']) * int(res['price']))
   context.user_data['fill_offer'] = res

   if res['offer_type'] == 'sell':
      update.message.reply_text(
         "Reply with your wallet address to receive {} {} from our escrow once your payments have been confirmed.".format(res['amount'], res['coin'])
      )
   elif res['offer_type'] == 'buy':
      update.message.reply_text(
         "Reply with your account details to receive NGN{} from our escrow once your transaction has been confirmed.".format(total)
      )
   else:
      update.message.reply_text(
         "Something went wrong, contact @fridai2000 for support"
      )


   return THREE

def confirm_fill(update, context):
   user = update.message.from_user
   bot = context.bot
   bot.send_chat_action(chat_id=user.id, action=ChatAction.TYPING)

   text = update.message.text
   fill_offer = context.user_data['fill_offer']
   bot_master_id = 984989153
   # ## setup send text to bot_master
   bot.send_message(
      chat_id=bot_master_id,
      text="An offer is being filled by {} tgram_uid: {}, confirm\n\nFillers Details: {}".format(user.first_name, user.id, text)
   )

   # confirm fill keyboard
   keyboard = [
      [InlineKeyboardButton("CONFIRM", callback_data='confirm')]
   ]

   confirm_fill_keyboard = InlineKeyboardMarkup(keyboard)

   # send message to owner of the offer
   bot.send_message(
      chat_id=fill_offer['tgram_uid'],
      text="Your {} offer for {} {} is currently being filled please stand by for confirmation".format(fill_offer['offer_type'], fill_offer['amount'], fill_offer['coin']),
      reply_markup=confirm_fill_keyboard
   )

   total = (float(fill_offer['amount']) * int(fill_offer['price']))


   if fill_offer['offer_type'] == 'sell':
      update.message.reply_text(
         "Please proceed to credit {} with the amount of NGN{}. Then send a screenshot of the transaction to @fridai2000 for confirmation\n\nOnce your transaction has been confirmed the {} {} in escrow will be automatically sent to you.".format(fill_offer['fill_method'], round(total, 2), fill_offer['amount'], fill_offer['coin'])
      )
   elif res['offer_type'] == 'buy':
      update.message.reply_text(
         "Please proceed to send {} {} to the following wallet address {}. Then send a screenshot of the transaction to @fridai2000 for confirmation\n\nOnce your transaction has been confirmed the total of NGN{} in escrow will be automatically sent to you.".format(fill_offer['amount'], fill_offer['coin'], fill_offer['fill_method'], round(total, 2))
      )
   else:
      update.message.reply_text(
         "Something went wrong, contact @fridai2000 for support"
      )

   return END

# def transactions(update, context):
   # show the curenctly pending list of transactions
