from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart, Command
from menu.mainkb import kb_generation, like_dislike_kb

from utils.states import Main_Form
from data.mongodb import DataBase
from main import bot
from data.language import language_texts
from config import uri


router = Router()
db = DataBase(uri)

# /start Command handler
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.from_user.username == None:
        await message.answer('You must have a username to use this service.')
    else:
        try:
            lang = await db.get_one(message.from_user.id, 'lang')
        except Exception:
            lang = '🇷🇺 Русский'
        await state.set_state(Main_Form.lang)
        await message.answer(language_texts[lang]['choose_lang_t'], reply_markup=kb_generation(['🇷🇺 Русский', '🇺🇦 Українська', '🇬🇧 English'], one_time=True))

# /myprofile Command handler
@router.message(Command('myprofile'))
async def myprofile(message: Message, state: FSMContext):
    if message.from_user.username == None:
        await message.answer('You must have a username to use this service.')
    else:
        await state.set_state(Main_Form.buttons)
        try:
            data = await db.get_full_data(message.from_user.id)
            lang = await db.get_one(message.from_user.id, 'lang')
        except Exception:
            await message.answer(language_texts['🇷🇺 Русский']['noprofile_t'], reply_markup=kb_generation('/start'))
        else:
            await message.answer_photo(photo=data[1], caption=data[0])
            await message.answer(language_texts[lang]['menu_t'], reply_markup=kb_generation(['1', '2', '3', '4']))
        
# /language Command handler
@router.message(Command('language'))
async def lang(message: Message, state: FSMContext):
    if message.from_user.username == None:
        await message.answer('You must have a username to use this service.')
    else:
        try:
            lang_user = await db.get_one(message.from_user.id, 'lang')
        except Exception:
            await message.answer(language_texts['🇷🇺 Русский']['noprofile_t'], reply_markup=kb_generation('/start'))
        else:
            await state.set_state(Main_Form.update_lang)
            await message.answer(language_texts[lang_user]['choose_lang_t'], reply_markup=kb_generation(['🇷🇺 Русский', '🇺🇦 Українська', '🇬🇧 English']))

# Additional func needs to update language
@router.message(Main_Form.update_lang)
async def update_lang(message: Message):
    querry = {'lang': message.text}
    await db.update_one(message.from_user.id, querry)
    await message.answer(language_texts[message.text]['updated_t'], reply_markup=ReplyKeyboardRemove())

# The quiz starts here with first question about user language and age
@router.message(Main_Form.lang)
async def lang_state(message: Message, state: FSMContext):
    if message.text not in ['🇷🇺 Русский', '🇺🇦 Українська', '🇬🇧 English']:
        await message.answer('*-*', reply_markup=kb_generation(['🇷🇺 Русский', '🇺🇦 Українська', '🇬🇧 English']))
        await state.set_state(Main_Form.lang)
    else: 
        await db.update_one(message.from_user.id, {'lang': message.text})
        try:
            lang = await db.get_one(message.from_user.id, 'lang')
        except Exception:
            lang = message.text
        await state.update_data(lang=message.text)
        await state.set_state(Main_Form.age)
        await state.update_data(lang=lang)
        await message.answer(language_texts[lang]['age_q'])

# Confirming age and ask about user gender
@router.message(Main_Form.age)
async def age_state(message: Message, state: FSMContext):
    lang = (await state.get_data())['lang']

    if message.text.isdigit():
        await state.update_data(age=message.text)
        await state.set_state(Main_Form.your_gender)
        await message.answer(language_texts[lang]['gender_q'], reply_markup=kb_generation(language_texts[lang]['gender_bt']))
    else:
        await message.answer(language_texts[lang]['age_q'])
        await state.set_state(Main_Form.age)

# Confirming user gender and ask about user interest of gender
@router.message(Main_Form.your_gender)
async def user_gender_state(message: Message, state: FSMContext):
    lang = (await state.get_data())['lang']

    if message.text in ['Я парень', 'Я девушка', 'Я хлопець', 'Я дівчина', 'I\'m a guy', 'I\'m a girl']: 
        await state.update_data(your_gender=message.text)
        await state.set_state(Main_Form.opponent_gende)
        await message.answer(language_texts[lang]['interests_q'], reply_markup=kb_generation(language_texts[lang]['interests_bt'], one_time=True))
    else:
        await message.answer(language_texts[lang]['gender_q'], reply_markup=kb_generation(language_texts[lang]['gender_bt']))
        await state.set_state(Main_Form.your_gender)

# Confirming interest of gender and ask about user city
@router.message(Main_Form.opponent_gende)
async def opponent_gender_state(message: Message, state: FSMContext):
    lang = (await state.get_data())['lang']

    if message.text in ['Парни', 'Девушки', 'Хлопці', 'Дівчата', 'Guys', 'Girls']:
        await state.update_data(opponent_gende=message.text)
        await state.set_state(Main_Form.city)
        await message.answer(language_texts[lang]['city_q'])
    else:
        await message.answer(language_texts[lang]['interests_q'], reply_markup=kb_generation(language_texts[lang]['interests_bt'], one_time=True))
        await state.set_state(Main_Form.opponent_gende) 

# Confirming user city and ask about username
@router.message(Main_Form.city)
async def city_state(message: Message, state: FSMContext):
    lang = (await state.get_data())['lang']

    if message.text.isalpha():
        await state.update_data(city=message.text)
        await state.set_state(Main_Form.name)
        await message.answer(language_texts[lang]['name_q'], reply_markup=kb_generation(message.from_user.first_name))
    else:
        await message.answer(language_texts[lang]['city_q'])
        await state.set_state(Main_Form.city) 

# Confirming username and ask about user description
@router.message(Main_Form.name)
async def name_state(message: Message, state: FSMContext):
    try:
        lang = await db.get_one(message.from_user.id, 'lang')
    except Exception:
        lang = (await state.get_data())['lang']
    await state.update_data(name=message.text)
    await state.set_state(Main_Form.about_info)
    await message.answer(language_texts[lang]['about_t'], reply_markup=kb_generation(language_texts[lang]['skp_t']))

# Confirming user description and ask about user photo
@router.message(Main_Form.about_info)
async def info_state(message: Message, state: FSMContext):
    try:
        lang = await db.get_one(message.from_user.id, 'lang')
    except Exception:
        lang = (await state.get_data())['lang']
    if message.text == language_texts[lang]['skp_t']:
        await state.update_data(about_info='')
    else:
        await state.update_data(about_info=message.text)
    await state.set_state(Main_Form.photo)
    await message.answer(language_texts[lang]['photo_q'], reply_markup=ReplyKeyboardRemove())

# Confirming user photo and make user data from quiz
@router.message(Main_Form.photo, F.photo)
async def photo_state(message: Message, state: FSMContext):
    photo_user = message.photo[-1].file_id
    await state.update_data(photo=photo_user)
    await state.set_state(Main_Form.result)

    data = await state.get_data()

    name = data['name']
    old = data['age']
    about = data['about_info']
    if about:
        about = '- '+about
    try:
        lang = data['lang']
    except KeyError:
        print('Keyerror')
        lang = await db.get_one(message.from_user.id, 'lang')
    user_gender = data['your_gender']
    opponent_gender = data['opponent_gende']
    city = data['city']


    #name, age, chups city - description
    await db.add_user(user_id=message.from_user.id, lang=lang, name=name, old=old, gender=user_gender, 
                interests=opponent_gender, city=city, info=about, photo=photo_user)
    user_info = f'{name.title()}, {old} 📍 {about}'

    await message.answer_photo(photo=photo_user, caption=user_info)
    await message.answer(language_texts[lang]['right_q'], reply_markup=kb_generation(language_texts[lang]['right_bt'], one_time=True))

# Results user quiz data with 4 buttons (1-change again, 2-change visibillity, 3-change description, 4-search person)
@router.message(Main_Form.result)
async def result_state(message: Message, state: FSMContext):
    try:
        lang = await db.get_one(message.from_user.id, 'lang')
    except Exception:
        lang = (await state.get_data())['lang']
    if message.text == language_texts[lang]['right_bt'][1]:
        await state.update_data(result=message.text)
        await state.set_state(Main_Form.age)
        await message.answer(language_texts[lang]['age_q'])
    else: 
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=(message.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=(message.message_id)-1)
        except Exception:
            print("An error occurred")
        await state.set_state(Main_Form.buttons)
        await message.answer(language_texts[lang]['menu_t'], reply_markup=kb_generation(['1', '2', '3', '4']))

# Buttons handler (1-change again, 2-change visibillity, 3-change description, 4-search person)
@router.message(Main_Form.buttons)
async def ends_state(message: Message, state: FSMContext):
    lang = await db.get_one(message.from_user.id, 'lang')
    if message.text == '1':
        await state.set_state(Main_Form.lang)
        await message.answer(language_texts[lang]['choose_lang_t'], reply_markup=kb_generation(['🇷🇺 Русский', '🇺🇦 Українська', '🇬🇧 English'], one_time=True))
    elif message.text == '2':
        is_visible = await db.get_visible(user_id=message.from_user.id)
        print(is_visible)

        if is_visible:

            await message.answer(language_texts[lang]['visible_0'])
            await db.change_visibility(user_id=message.from_user.id)
        else:
            await message.answer(language_texts[lang]['visible_1'])
            await db.change_visibility(user_id=message.from_user.id)

    elif message.text == '3':
        await message.answer(language_texts[lang]['info_t'], reply_markup=kb_generation(language_texts[lang]['skp_t']))
        await state.set_state(Main_Form.description)
    elif message.text == '4':
        match = await db.find_match(user_id=message.from_user.id)
        if match is False:
            await message.answer(language_texts[lang]['noprofiles_t'])
        else:
            opponent_id = match['_id']
            data = await db.get_full_data(opponent_id)

            await state.update_data(buttons=opponent_id)
            await message.answer_photo(photo=data[1], caption=data[0], reply_markup=like_dislike_kb(id_match=str(opponent_id), nickname=message.chat.username))

# Callback handler with like dislike data
@router.callback_query(F.data)
async def calll(call: CallbackQuery):
    lang = await db.get_one(call.from_user.id, 'lang')
    user2, nickname2  = call.data[4:].split()
    user2 = int(user2)
    if call.data.startswith('like'):
        await db.add_love(call.from_user.id, user_id2=user2)
        if await db.time_to_love(call.from_user.id, user_id2=user2) == True:
            try:
                await call.message.delete()
            except Exception:
                print("An error occurred")
            await bot.send_message(chat_id=user2, text=language_texts[lang]['match_t'])

            data = await db.get_full_data(user2)
            data2 = await db.get_full_data(call.from_user.id)

            await bot.send_photo(photo=data2[1], caption=data2[0]+f'\n@{call.from_user.username}', chat_id=user2)
            await call.message.answer(text=language_texts[lang]['match_t'])
            await call.message.answer_photo(photo=data[1], caption=data[0]+f'\n@{nickname2}')

            await db.update_dislike_users(call.from_user.id, user2)
            await db.update_dislike_users(user2, call.from_user.id)
        else:
            data = await db.get_full_data(call.from_user.id)
            try:
                await call.message.delete() 
            except Exception:
                print("An error occurred")
            await call.message.answer(language_texts[lang]['liked_t'])

            await bot.send_photo(chat_id=user2, photo=data[1], caption=data[0], reply_markup=like_dislike_kb(id_match=str(call.from_user.id), nickname=call.message.chat.username))
    else:
        try:
            await call.message.delete()
        except Exception:
            print("An error occurred")
        await db.update_dislike_users(call.from_user.id, user2)
        print(f'{call.from_user.id}, {user2}')
        await db.update_dislike_users(user2, call.from_user.id)
        await call.message.answer(language_texts[lang]['dislike_t'])

# Description change handler
@router.message(Main_Form.description)
async def desc(message: Message, state: FSMContext):
    lang = await db.get_one(message.from_user.id, 'lang')
    if message.text == language_texts[lang]['skp_t']:
        data = ''
    else:
        data = message.text
    querry = {
        'info': data
    }
    await db.update_one(message.from_user.id, querry)
    await message.answer(language_texts[lang]['updated_t'])

    await state.set_state(Main_Form.buttons)

    data = await db.get_full_data(message.from_user.id)
    await message.answer_photo(photo=data[1], caption=data[0])
    await message.answer(language_texts[lang]['menu_t'], reply_markup=kb_generation(['1', '2', '3', '4']))
