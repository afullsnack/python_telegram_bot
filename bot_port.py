#Main  state handler for LBOT


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import logging
import pprint

END = ConversationHandler.END
# import crypto price API
from api import get_spot
# trade handler script
from trade import Trade
import time

# import escrow handlers
from escrow import offer, help, buy, sell, confirm, get_details, fill, confirm_fill, show, OFFER_START, ONE, TWO, THREE

# import database functions
from db import BinaryDB

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#Main components of the algorithm
BINARY_MAIN, SECOND, THIRD, FOURTH = range(4)
WITHDRAW_AMOUNT, WITHDRAW_ACCOUNT = range(2)
DEPOSIT_AMOUNT, LINK = range(2)


button_states = {
	"BINARY_MAIN": [
		[
			InlineKeyboardButton("BALANCE", callback_data='balance')
		],
		[
			InlineKeyboardButton("WITHDRAW", callback_data='withdraw'),
			InlineKeyboardButton("DEPOSIT", callback_data='deposit')
		],
		[
			InlineKeyboardButton("START TRADE", callback_data='start_trade'),
			# InlineKeyboardButton("VIEW ASSETS", callback_data='view_assets')
		],
		[
			InlineKeyboardButton("CLOSE", callback_data='close')
		]
	],
	"SECOND": {
		"BALANCE": [
			[
				InlineKeyboardButton("ACTIVATE NGN ACCOUNT", callback_data='activate_ngn')
			],
			[
				InlineKeyboardButton("ACTIVATE DEMO ACCOUNT", callback_data='activate_demo')
			],
			[
				InlineKeyboardButton("BACK", callback_data='main_back')
			]
		],
		"WITHDRAW": [
			[
				InlineKeyboardButton("CANCEL", callback_data='cancel')
			]
		],
		"DEPOSIT": [
			[
				InlineKeyboardButton("CANCEL", callback_data='cancel')
			]
		],
    "TIME_SETTINGS": [
      [
        InlineKeyboardButton("5mins", callback_data='5'),
        InlineKeyboardButton("10mins", callback_data='10'),
        InlineKeyboardButton("15mins", callback_data='15'),
      ],
      [
        InlineKeyboardButton("BACK", callback_data='main_back')
      ]
    ],
    "TRADE": [
      [
        InlineKeyboardButton("BTC", callback_data='btc'),
        InlineKeyboardButton("ETH", callback_data='eth'),
        InlineKeyboardButton("XMR", callback_data='xrp')
      ],
      [
        InlineKeyboardButton("BACK", callback_data='main_back')
      ]
    ],
    "ASSETS": [
      [
        InlineKeyboardButton("BACK", callback_data='main_back')
      ]
    ]
	},
  "THIRD": {
    "ACTIVATE_NGN": [
      [
        InlineKeyboardButton("BACK", callback_data='balance_back')
      ]
    ],
    "ACTIVATE_DEMO": [
      [
        InlineKeyboardButton("BACK", callback_data='balance_back')
      ]
    ],
    "WITHDRAW_AMOUNT": [
      [
        InlineKeyboardButton("30%", callback_data='30'),
        InlineKeyboardButton("60%", callback_data='60'),
        InlineKeyboardButton("100%", callback_data='100')
      ],
      [
        InlineKeyboardButton("BACK", callback_data='withdraw_back')
      ]
    ],
    "WITHDRAW_ADDRESS": [
      [
        InlineKeyboardButton("CANCEL", callback_data='cancel')
      ]
    ],
    "SHOW_ADDRESS": [
      [
        InlineKeyboardButton("CANCEL", callback_data='cancel')
      ]
    ],
    "TRADE_OPTIONS": [
      [
        InlineKeyboardButton("CALL", callback_data='call'),
        InlineKeyboardButton("PUT", callback_data='put')
      ],
      [
        InlineKeyboardButton("RELOAD PRICE", callback_data='reload')
      ],
      [
        InlineKeyboardButton("BACK", callback_data='trade_back')
      ]
    ]
  },
  "FOURTH": {
    "INIT_TRADE": [
      [
        InlineKeyboardButton("TRADE AGAIN", callback_data='trade_back')
      ],
      {
        InlineKeyboardButton("MAIN MENU", callback_data="main_back")
      }
    ]
  }
}

main_menu = [
  ['BINARY OPTIONS TRADE'],
  ['BUY/SELL CRYPTOCURRENCY']
]

def start(update, context):
	user = update.message.from_user

	reply_markup = ReplyKeyboardMarkup(main_menu, one_time_keyboard=False, resize_keyboard=True)

	update.message.reply_text(
		"{}, welcome to Oreo Crypt.\n\nThis bot helps you trade binary options and also acquire bitcoin and other crypto currencies\n\n".format(user.first_name),
		reply_markup=reply_markup
	)

# entry to the binary tradeing path
def binary(update, context):
  user = update.message.from_user
  bot = context.bot
  bot.send_chat_action(chat_id=user.id, action=ChatAction.TYPING)
  binary_db = BinaryDB()
  res = binary_db.create_user(user.id, user.first_name, user.last_name)
  context.user_data['default_acct'] = res['active_acct']

  reply_markup = InlineKeyboardMarkup(button_states['BINARY_MAIN'])

  update.message.reply_text(
    "Welcome {} to our simple binary options trading platform\n\nYou will currently be using a DEMO account with 10000 credits to trade until you make a deposit, go to the deposit menu to see how you can deposit.\n\n".format(user.first_name),
    reply_markup=reply_markup
  )

  return BINARY_MAIN

# The back handler functions -- START --
def back_main(update, context):
  user = update.effective_chat
  query = update.callback_query
  bot = context.bot

  keyboard = button_states['BINARY_MAIN']
  reply_markup = InlineKeyboardMarkup(keyboard)

  bot.edit_message_text(
    chat_id=query.message.chat_id,
    message_id=query.message.message_id,
    text="Welcome {} to our simple binary options trading platform\n\nYou will currently be using a DEMO account with 10000 credits to trade until you make a deposit, go to the deposit menu to see how you can deposit.\n\n".format(user.first_name),
    reply_markup=reply_markup
  )

  return BINARY_MAIN

def back_balance(update, context):
	user = update.effective_chat
	query = update.callback_query
	bot = context.bot
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

	keyboard = button_states['SECOND']['BALANCE']
	reply_markup = InlineKeyboardMarkup(keyboard)

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="{}, Select an item below".format(user.first_name),
		reply_markup=reply_markup
	)

	return SECOND

def back_withdraw(update, context):
  user = update.effective_chat
  query = update.callback_query
  bot = context.bot

  keyboard = button_states['BINARY_MAIN']
  reply_markup = InlineKeyboardMarkup(keyboard)

  bot.edit_message_text(
    chat_id=query.message.chat_id,
    message_id=query.message.message_id,
    text="Welcome {} to our simple binary options trading platform\n\nYou will currently be using a DEMO account with 10000 credits to trade until you make a deposit, go to the deposit menu to see how you can deposit.\n\n".format(user.first_name),
    reply_markup=reply_markup
  )

  return END

def back_deposit(update, context):
  user = update.effective_chat
  query = update.callback_query
  bot = context.bot

  keyboard = button_states['BINARY_MAIN']
  reply_markup = InlineKeyboardMarkup(keyboard)

  bot.edit_message_text(
    chat_id=query.message.chat_id,
    message_id=query.message.message_id,
    text="Welcome {} to our simple binary options trading platform\n\nYou will currently be using a DEMO account with 10000 credits to trade until you make a deposit, go to the deposit menu to see how you can deposit.\n\n".format(user.first_name),
    reply_markup=reply_markup
  )

  return END

def back_trade(update, context):
  user = update.effective_chat
  query = update.callback_query
  bot = context.bot
  context.user_data['asset'] = None

  reply_markup = InlineKeyboardMarkup(button_states['SECOND']['TRADE'])

  bot.edit_message_text(
    chat_id=query.message.chat_id,
    message_id=query.message.message_id,
    text="<b>PICK AN ASSET TO TRADE</b>\n<b>Note:</b> %PROFIT ON ALL ASSET AT THIS TIME IS 80%",
    reply_markup=reply_markup,
    parse_mode=ParseMode.HTML
  )

  return SECOND

def back_assets(update, context):
  user = update.effective_chat
  query = update.callback_query
  bot = context.bot

  keyboard = button_states['SECOND']['ASSETS']
  reply_markup = InlineKeyboardMarkup(keyboard)

  bot.edit_message_text(
    chat_id=query.message.chat_id,
    message_id=query.message.message_id,
    text="{}, Select on item below".format(user.first_name),
    reply_markup=reply_markup
  )

  return SECOND

def back_init(update, context):
	query = update.callback_query
	bot = context.bot
	chat = update.effective_chat
	text = ""

	reply_markup = InlineKeyboardMarkup(button_states['THIRD']['TRADE_OPTIONS'])

	if 'asset' in context.user_data and context.user_data['asset'] == 'btc':
		text = "BTC/USD - " + get_spot('BTC-USD')
	elif 'asset' in context.user_data and context.user_data['asset'] == 'eth':
		text = "ETH/USD - " + get_spot('ETH-USD')
	elif 'asset' in context.user_data and context.user_data['asset'] == 'xrp':
		text = "XRP/USD - " + get_spot('XRP-USD')
	else:
		text = "there was a problem"

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="<b>%PROFIT ON CURRENT ASSET IS 80%</b> \n\n{}".format(text),
		reply_markup=reply_markup,
		parse_mode=ParseMode.HTML
	)

	return THIRD

# The back handler functions -- END --

#This is the profile conversation path
def balance(update, context):
	query = update.callback_query
	bot = context.bot
	user_id = query.message.chat_id
	bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

	# database functions
	binary_db = BinaryDB()
	res = binary_db.db.users.find_one({"tgram_uid": user_id}, ['account'])
	# print(res)
	demo_bal = res['account']['demo_balance']
	ngn_bal = res['account']['ngn_balance']

	context.user_data['demo_bal'] = demo_bal

	reply_markup = InlineKeyboardMarkup(button_states['SECOND']['BALANCE'])

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="<b>YOUR ACCOUNT BALANCES:</b>\n\nDEMO BALANCE:  <b>{}</b>\n\nNGN BALANCE:  <b>{}</b>\n\n".format(demo_bal, ngn_bal),
		reply_markup=reply_markup,
		parse_mode=ParseMode.HTML
	)

	return SECOND

def activate_ngn(update, context):
	query = update.callback_query
	bot = context.bot

	# database functions
	binary_db = BinaryDB()

	# check if a deposit has been made into the the ngn account
	res = binary_db.db.users.find_one({"tgram_uid": query.message.chat_id}, ['account'])
	if res['account']['ngn_balance'] <= 0:
		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="You have to make a deposit before activating your NGN account",
			reply_markup=reply_markup
		)

		return THIRD

	res = binary_db.switch_acount(query.message.chat_id, 'ngn')
	print(res)
	context.user_data['default_acct'] = res['active_acct']

	reply_markup = InlineKeyboardMarkup(button_states['THIRD']['ACTIVATE_NGN'])

		#GET TRADE HISTORY OF THE USER AND RETURN
	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="Your NGN account is currently active and set to default trade account",
		reply_markup=reply_markup
	)

	return THIRD

# set base currency of the user
def activate_demo(update, context):
	query = update.callback_query
	chat_id = query.message.chat_id
	bot = context.bot
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

	# database functions
	binary_db = BinaryDB()
	res = binary_db.switch_acount(query.message.chat_id, 'demo')
	print(res)
	context.user_data['default_acct'] = res['active_acct']

	reply_markup = InlineKeyboardMarkup(button_states['THIRD']['ACTIVATE_DEMO'])

	if context.user_data['demo_bal'] <= 100:
		res = binary_db.db.users.find_one_and_update({"tgram_uid"}, {'$set': {"account.demo_balance": 10000}})
		print(res)
		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="Your DEMO account is currently active and REFRESHED, and set to default trade account",
			reply_markup=reply_markup
		)

		return THIRD

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="Your DEMO account is currently active and set to default trade account",
		reply_markup=reply_markup
	)
	return THIRD

#This is the withdraw conversation path
def withdraw(update, context):
	query = update.callback_query
	chat_id = query.message.chat_id
	bot = context.bot
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

	binary_db = BinaryDB()
	res = binary_db.db.users.find_one({"tgram_uid": query.message.chat_id}, ['active_acct', 'account'])

	reply_markup = InlineKeyboardMarkup(button_states['SECOND']['WITHDRAW'])


	if res['account']['ngn_balance'] == None or res['account']['ngn_balance'] == 0:
		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="Sorry you do not have any funds to withdraw at this time",
			reply_markup=reply_markup
		)

		return WITHDRAW_AMOUNT


	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="Reply with the amount you want to withdraw",
		reply_markup=reply_markup
	)

	return WITHDRAW_AMOUNT
# withdraw amount handler function
def withdraw_amount(update, context):
	# query = update.callback_query
	bot = context.bot
	chat_id = update.message.chat_id
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
	text = update.message.text
	print(text)

	reply_markup = InlineKeyboardMarkup(button_states['THIRD']['WITHDRAW_AMOUNT'])

	bot.send_message(
		chat_id=chat_id,
		# message_id=query.message.message_id,
		text="Reply with your bank account details",
		reply_markup=reply_markup
	)

	return WITHDRAW_ACCOUNT

# withdraw address handler function
def withdraw_account(update, context):
	# query = update.callback_query
	bot = context.bot
	chat_id = update.message.chat_id
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
	text = update.message.text
	print(text)

	reply_markup = InlineKeyboardMarkup(button_states['THIRD']['WITHDRAW_ADDRESS'])

	bot.send_message(
		chat_id=chat_id,
		# message_id=query.message.message_id,
		text="Your account details have been saved, and your withdraw request under review\n\nWithdrawals will take upto 24hrs to complete",
		reply_markup=reply_markup
	)

	return END

#This is the deposit conversation path
def deposit(update, context):
	query = update.callback_query
	bot = context.bot

	reply_markup = InlineKeyboardMarkup(button_states['SECOND']['DEPOSIT'])

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="Reply with the amount you wish to deposit",
		reply_markup=reply_markup
	)

	return DEPOSIT_AMOUNT

# show deposit address handler function
def deposit_amount(update, context):
	# query = update.callback_query
	bot = context.bot
	chat_id = update.message.chat_id
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
	text = update.message.text
	print(text)

	binary_db = BinaryDB()
	res = binary_db.deposit(chat_id, text)
	print(res)

	reply_markup = InlineKeyboardMarkup(button_states['THIRD']['SHOW_ADDRESS'])

	bot.send_message(
		chat_id=chat_id,
		# message_id=query.message.message_id,
		text="Follow the link to deposit your stipulated amount https://paystack.com/pay/oreo-binary",
		reply_markup=reply_markup
	)

	return LINK

#This is the trade conversation path
def trade_time(update, context):
	query = update.callback_query
	chat_id = query.message.chat_id
	bot = context.bot
	bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

	binary_db = BinaryDB()
	res = binary_db.db.users.find_one({"tgram_uid": chat_id})
	total_bal = res['account']['demo_balance'] if res['active_acct'] == 'demo' else res['account']['ngn_balance']
	context.user_data['total_bal'] = total_bal

	reply_markup = InlineKeyboardMarkup(button_states['SECOND']['TIME_SETTINGS'])

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="PICK A DURATION FOR THE TRADE",
		reply_markup=reply_markup
	)

	return SECOND

# settings for the trade such as duration, amount
def trade_amount(update, context):
  query = update.callback_query
  bot = context.bot

#   print(query.data)
  context.user_data['trade_time'] = int(query.data)


  bot.edit_message_text(
    chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="<b>REPLY WITH AN AMOUNT TO TRADE WITH</b>",
		parse_mode=ParseMode.HTML
  )

  return SECOND

def trade(update, context):
	# query = update.callback_query
	chat_id = update.message.chat_id
	bot = context.bot
	
	# print(update.message.text)
	context.user_data['trade_amount'] = int(update.message.text)
	main_menu = InlineKeyboardMarkup([[InlineKeyboardButton("MAIN MENU", callback_data='main_menu')]])

	# check if the total_bal is over the trade_amount
	if context.user_data['total_bal'] < context.user_data['trade_amount']:
		bot.send_message(
			chat_id=chat_id,
			text="YOU HAVE INSUFFICIENT BALANCE FOR THIS TRANSACTION\n\nPLEASE MAKE A DEPOSIT OR GO TO BALANCE AND ACTIVATE DEMO ACCOUNT TO GET A REFRESH",
			reply_markup=main_menu
		)
		return BINARY_MAIN

	reply_markup = InlineKeyboardMarkup(button_states['SECOND']['TRADE'])

	bot.send_message(
		chat_id=chat_id,
		# message_id=query.message.message_id,
		text="<b>PICK AN ASSET TO TRADE</b>\n\n<b>Note:</b> %PROFIT ON ALL ASSET AT THIS TIME IS 80%",
		reply_markup=reply_markup,
		parse_mode=ParseMode.HTML
	)

	return SECOND

# ** The trade assets price functionality tests
def trade_option(update, context):
  query = update.callback_query
  bot = context.bot
  chat = update.effective_chat
  text = ""

  reply_markup = InlineKeyboardMarkup(button_states['THIRD']['TRADE_OPTIONS'])

  if query.data == 'btc' or context.user_data['asset'] == 'btc':
    context.user_data['asset'] = query.data if query.data == 'btc' else context.user_data['asset']
    context.user_data['currency'] = 'BTC-USD'
    text = "BTC/USD - " + get_spot('BTC-USD')
  elif query.data == 'eth' or context.user_data['asset'] == 'eth':
    context.user_data['asset'] = query.data if query.data == 'eth' else context.user_data['asset']
    context.user_data['currency'] = 'ETH-USD'
    text = "ETH/USD - " + get_spot('ETH-USD')
  elif query.data == 'xrp' or context.user_data['asset'] == 'xrp':
    context.user_data['asset'] = query.data if query.data == 'xrp' else context.user_data['asset']
    context.user_data['currency'] = 'XRP-USD'
    text = "XRP/USD - " + get_spot('XRP-USD')
  else:
    text = "there was a problem"

  bot.edit_message_text(
    chat_id=query.message.chat_id,
    message_id=query.message.message_id,
    text="<b>%PROFIT ON CURRENT ASSET IS 80%</b> \n\n{}".format(text),
    reply_markup=reply_markup,
    parse_mode=ParseMode.HTML
  )

  return THIRD


# handles the actual trading process of an assets
def init_trade(update, context):
	query = update.callback_query
	bot = context.bot
	chat = update.effective_chat
	asset = context.user_data['asset']
	currency = context.user_data['currency']
	trade_time = context.user_data['trade_time']
	trade_amount = context.user_data['trade_amount']
	total_bal = context.user_data['total_bal']
	default_acct = context.user_data['default_acct']

  

	reply_markup = InlineKeyboardMarkup(button_states['FOURTH']['INIT_TRADE'])

	if query.data == 'call':
		t = Trade(60*trade_time, trade_amount, total_bal, 'CALL')
		bet_quote = t.get_price(currency)
		first = "SPOT QUOTE: <b>$" + str(round(bet_quote, 4)) + "</b>\nTRADE TYPE: <b>"+ t.trade_type+"</b>"
		result = None

		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text=first,
			# reply_markup=reply_markup,
			parse_mode=ParseMode.HTML
		)

		last_quote = bet_quote

		for i in range(0, t.duration, 5):
			current_quote = t.get_price(currency)
			first = "SPOT QUOTE: <b>$"+ str(round(bet_quote, 4)) +"</b>\nCURRENT QUOTE: <b>$" + str(round(current_quote, 4)) +"</b>\nTRADE TYPE: <b>"+ t.trade_type+"</b>"
			if(i >= t.duration):
				break
			result = t.call(bet_quote, current_quote, 80)

			if current_quote != last_quote:
				bot.send_message(    
					chat_id=query.message.chat_id,
					message_id=query.message.message_id,
					text=first + "\n\n" + result['state'],
					# reply_markup=reply_markup,
					parse_mode=ParseMode.HTML
				)
				last_quote = current_quote

			time.sleep(5)
			i+=5

		bot.send_message(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="<b>TRADE IS DONE!!!</b>"+ "\n\n" + result['state'],
			reply_markup=reply_markup,
			parse_mode=ParseMode.HTML
		)
		binary_db = BinaryDB()
		res = binary_db.db.users.update_one({"tgram_uid": query.message.chat_id}, {'$set': {"account.demo_balance": result['new_balance'] }}) if default_acct == 'demo' else binary_db.db.users.update_one({"tgram_uid": query.message.chat_id}, {'$set': {"account.ngn_balance": result['new_balance'] }})
		print(res)
    
	else:
		t = Trade(60*trade_time, trade_amount, total_bal, 'PUT')
		bet_quote = t.get_price(currency)
		first = "SPOT QUOTE: <b>$" + str(round(bet_quote, 4)) +"</b>\nTRADE TYPE: <b>"+ t.trade_type+"</b>"
		result = None

		bot.edit_message_text(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text=first,
			# reply_markup=reply_markup,
			parse_mode=ParseMode.HTML
		)
		last_quote = bet_quote

		for i in range(0, t.duration, 5):
			current_quote = t.get_price(currency)
			first = "SPOT QUOTE: <b>$"+ str(round(bet_quote, 4)) +"</b>\nCURRENT QUOTE: <b>$" + str(round(current_quote, 4)) +"</b>\nTRADE TYPE: <b>"+ t.trade_type+"</b>"
			if(i >= t.duration):
				break
			result = t.put(bet_quote, current_quote, 80)

			if current_quote != last_quote:
				bot.send_message(
					chat_id=query.message.chat_id,
					message_id=query.message.message_id,
					text=first + "\n\n" + result['state'],
					# reply_markup=reply_markup,
					parse_mode=ParseMode.HTML
				)
				last_quote = current_quote

			time.sleep(5)
			i+=5

		bot.send_message(
			chat_id=query.message.chat_id,
			message_id=query.message.message_id,
			text="<b>TRADE IS DONE!!!</b>"+ "\n\n" + result['state'],
			reply_markup=reply_markup,
			parse_mode=ParseMode.HTML
		)
		binary_db = BinaryDB()
		res = binary_db.db.users.update_one({"tgram_uid": query.message.chat_id}, {'$set': {"account.demo_balance": result['new_balance'] }}) if default_acct == 'demo' else binary_db.db.users.update_one({"tgram_uid": query.message.chat_id}, {'$set': {"account.ngn_balance": result['new_balance'] }})
		print(res)

	return FOURTH


#This is the assets conversation path
def assets(update, context):
	query = update.callback_query
	bot = context.bot

	reply_markup = InlineKeyboardMarkup(button_states['SECOND']['ASSETS'])

	bot.edit_message_text(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="Assets with currently open trade will show here, check TRADE HISTORY in PROFILE for previously traded assets",
		reply_markup=reply_markup
	)

	return SECOND

def end(update, context):
	"""Returns `ConversationHandler.END`, which tells the
	ConversationHandler that the conversation is over"""

	query = update.callback_query
	bot = context.bot

	bot = context.bot
	bot.send_message(
		chat_id=query.message.chat_id,
		message_id=query.message.message_id,
		text="You can access the menu again by using the button grid below"
	)

	return ConversationHandler.END

def end_offer(update, context):

  update.message.reply_text(
    text="Access the menu to start again"
  )
  return ConversationHandler.END

def end_level(update, context):
	user = update.callback_query.from_user
	reply_markup = InlineKeyboardMarkup(button_states['BINARY_MAIN'])
	update.message.reply_text(
		text="Welcome {} to our simple binary options trading platform\n\nYou will currently be using a DEMO account with 10000 credits to trade until you make a deposit, go to the deposit menu to see how you can deposit.\n\n".format(user.first_name),
		reply_markup=reply_markup
	)
	return END

# confirmation of receipt buy offer owner
def offer_owner_confirm(update, context):
	query = update.callback_query
	bot = context.bot
	bot_master_id = 984989153

	bot.send_message(
		chat_id=bot_master_id,
		text="The offer owner {} with tgram_uid: {}, has confirmed receipt of funds".format(query.message.from_user.first_name, query.message.chat_id)
	)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
		# Create the Updater and pass it your bot's token.
		updater = Updater("1224731770:AAHB3sKgasoPhx32qRJ558ocASP9OlfD6UY", use_context=True)

		# Get the dispatcher to register handlers
		dp = updater.dispatcher

		# Setup conversation handler with the states FIRST and SECOND
		# Use the pattern parameter to pass CallbackQueries with specific
		# data pattern to the corresponding handlers.
		# ^ means "start of line/string"
		# $ means "end of line/string"
		# So ^ABC$ will only allow 'ABC'
		binary_handler = ConversationHandler(
			entry_points=[MessageHandler(Filters.regex('^BINARY OPTIONS TRADE$'), binary)],
			states={
				BINARY_MAIN: [
					CallbackQueryHandler(balance, pattern='balance'),
					ConversationHandler(
						entry_points=[
							CallbackQueryHandler(withdraw, pattern='withdraw')
						],
						states={
							WITHDRAW_AMOUNT: [
								MessageHandler(Filters.text, withdraw_amount),
								CallbackQueryHandler(back_withdraw, pattern='cancel')
							],
							WITHDRAW_ACCOUNT: [
								MessageHandler(Filters.text, withdraw_account),
								CallbackQueryHandler(back_withdraw, pattern='cancel')
							]
						},
						fallbacks=[CommandHandler('stop', end_level)],
						map_to_parent={
							END: BINARY_MAIN
						}
					),
					CallbackQueryHandler(trade_time, pattern='start_trade'),
					ConversationHandler(
						entry_points=[
							CallbackQueryHandler(deposit, pattern='deposit')
						],
						states={
							DEPOSIT_AMOUNT: [
								MessageHandler(Filters.text, deposit_amount),
								CallbackQueryHandler(back_deposit, pattern='cancel')
							],
							LINK: [
								CommandHandler('stop', end_level),
								CallbackQueryHandler(back_deposit, pattern='cancel')
							]
						},
						fallbacks=[CommandHandler('stop', end_level)],
						map_to_parent={
							END: BINARY_MAIN
						}
					),
					CallbackQueryHandler(assets, pattern='view_assets'),
					CallbackQueryHandler(end, pattern='close')
				],
				SECOND: [
					CallbackQueryHandler(activate_ngn, pattern='activate_ngn'),
					CallbackQueryHandler(activate_demo, pattern='activate_demo'),
					CallbackQueryHandler(trade_amount, pattern='5'),
					CallbackQueryHandler(trade_amount, pattern='10'),
					CallbackQueryHandler(trade_amount, pattern='15'),
					MessageHandler(Filters.text, trade),
					CallbackQueryHandler(trade_option, pattern='btc'),
					CallbackQueryHandler(trade_option, pattern='eth'),
					CallbackQueryHandler(trade_option, pattern='xrp'),
					CallbackQueryHandler(back_main, pattern='main_back')
				],
				THIRD: [
					CallbackQueryHandler(init_trade, pattern='call'),
					CallbackQueryHandler(init_trade, pattern='put'),
					CallbackQueryHandler(trade_option, pattern='reload'),
					CallbackQueryHandler(balance, pattern='balance_back'),
					# CallbackQueryHandler(back_withdraw, pattern='withdraw_back'),
					# CallbackQueryHandler(back_deposit, pattern='deposit_back'),
					CallbackQueryHandler(back_trade, pattern='trade_back'),
					CallbackQueryHandler(back_assets, pattern='assets_back')
				],
				FOURTH: [
					CallbackQueryHandler(back_init, pattern='init_back'),
					CallbackQueryHandler(back_main, pattern='main_back'),
					CallbackQueryHandler(back_trade, pattern='trade_back')
				]
			},
			fallbacks=[CommandHandler('stop', end)]
		)

		# the buy/sell crypto conversation handler
		offer_conv = ConversationHandler(
			entry_points=[MessageHandler(Filters.regex('^BUY/SELL CRYPTOCURRENCY$'), offer)],
			states={
			OFFER_START: [
				CommandHandler('help', help),
				CommandHandler('sell', sell, pass_args=True, pass_chat_data=True),
				CommandHandler('buy', buy, pass_args=True, pass_chat_data=True),
				CommandHandler('show', show, pass_args=True, pass_chat_data=True),
				CommandHandler('stop', end_offer)
			],
			ONE: [
				CommandHandler('help', help),
				CallbackQueryHandler(confirm, pattern='confirm-buy'),
				CallbackQueryHandler(confirm, pattern='confirm-sell'),
				CallbackQueryHandler(help ,pattern='close'),
				CommandHandler('fill', fill, pass_args=True, pass_chat_data=True),
				CommandHandler('stop', end_offer)
			],
			TWO: [
				CommandHandler('help', help),
				CommandHandler('stop', end_offer),
				MessageHandler(Filters.text, get_details),
			],
			THREE: [
				CommandHandler('help', help),
				CommandHandler('stop', end_offer),
				MessageHandler(Filters.text, confirm_fill),
			]
			},
			fallbacks=[CommandHandler('stop', end_offer)]
		)

		# Add ConversationHandler to dispatcher that will be used for handling
		# updates

		# start of the bot
		dp.add_handler(binary_handler)

    # add escrow convo handler to dispatcher
		dp.add_handler(offer_conv)
		dp.add_handler(CommandHandler('start', start))
		dp.add_handler(CallbackQueryHandler(offer_owner_confirm, pattern='confirm'))

		# log all errors
		dp.add_error_handler(error)

		# Start the Bot
		updater.start_polling()

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		updater.idle()


if __name__ == '__main__':
	main()