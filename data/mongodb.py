from json import loads, dumps
from random import sample
import motor.motor_asyncio


class DataBase:

    def __init__(self, uri: str) -> None:
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.collection = self.cluster.usersdata.users

    async def update_one(self, user_id: str, data: str) -> None:
        await self.collection.update_one({'_id': user_id}, {'$set': data})

    async def get_one(self, user_id: str, data: str) -> str:
        res = await self.collection.find_one({'_id':user_id})
        return res[data]

    async def add_user(self, user_id: str, lang: str, old: str, gender: str, 
                       interests: str, city: str, name: str, info: str, photo: str, 
                       privacity=1, bunned_id='[]', match_love='[]') -> None:
        if await self.check_user(user_id) == None:    
            pattern = {"_id": user_id,
                    "lang": lang,
                    "old": old,
                    "gender": gender,
                    "interests": interests,
                    "city": city,
                    "name": name,
                    "info": info,
                    "photo": photo,
                    "privacity": privacity,
                    "bunned_id": bunned_id,
                    "match_love": match_love}
            
            self.collection.insert_one(pattern)
            print('New user!')
        else:
            print('User already exists, updating...')
            await self.update_user(user_id, lang, old, gender, interests, city, name, info, photo)

    async def check_user(self, user_id: str) -> None|list:
        res = await self.collection.find_one({"_id": user_id})

        return res
    
    async def update_user(self, user_id: str, lang: str, old: str, gender: str, 
                          interests: str, city: str, name: str, info: str, photo: str) -> None:
        data = {
            'lang': lang,
            'old': old,
            'gender': gender,
            'interests': interests,
            'city': city,
            'name': name,
            'info': info,
            'photo': photo
        }
        await self.update_one(user_id, data)
        print('User updated!')
    
    async def get_visible(self, user_id: str) -> bool:
        res = await self.get_one(user_id, 'privacity')
        return res == True

    async def change_visibility(self, user_id: str) -> None:
        res = await self.get_one(user_id, 'privacity')
        if res:
            res = 0
        else:
            res = 1
        return await self.update_one(user_id, {'privacity': res})
    
    async def update_dislike_users(self, user_id: str, ban_id: str) -> None:
        res = await self.show_dislike_data(user_id)
        res.append(ban_id)

        res = list(set(res))

        await self.update_one(user_id, {'bunned_id': dumps(res)})

    async def show_dislike_data(self, user_id: str) -> list:
        res = loads(await self.get_one(user_id, 'bunned_id'))
        return res

    async def find_match(self, user_id: str) -> dict|bool:
        interests = await self.get_one(user_id, 'interests')
        if interests in ['Девушки', 'Дівчата', 'Girls']: 
            gender_look = ["Я девушка", 'Я дівчина', 'I\'m a girl']
        else:
            gender_look = ['Я парень', 'Я хлопець', 'I\'m a guy']
        banned_users = await self.show_dislike_data(user_id)

        city = await self.get_one(user_id, 'city')

        query = {
                '_id': {'$nin': banned_users, '$ne': user_id},
                'city': city,
                'gender': {'$in': gender_look}, 
                'privacity': 1
            }

        res = await self.collection.find(query).to_list(length=None)

        if res:
            return sample(res, 1)[0]
        return False
    
    async def add_love(self, user_id: str, user_id2: str) -> None:
        if await self.check_love(user_id, user_id2) == False:
            res = loads(await self.get_one(user_id, 'match_love'))
            res.append(user_id2)
            await self.update_one(user_id, {'match_love': dumps(res)})

    async def check_love(self, user_id: str, user_id2: str) -> bool:
        res = loads(await self.get_one(user_id, 'match_love'))
        if user_id2 in res:
            return True
        return False
    
    async def time_to_love(self, user_id: str, user_id2: str) -> bool:
        res1 = loads(await self.get_one(user_id, 'match_love'))
        res2 = loads(await self.get_one(user_id2, 'match_love'))

        if user_id2 in res1 and user_id in res2:
            return True
        
    async def get_full_data(self, user_id: str) -> tuple:
        res = await self.collection.find_one({'_id': user_id})

        name = res['name']
        age = res['old']
        desc = res['info']

        photo = res['photo']

        description = f'{name.title()}, {age} 📍 {desc}'

        return (description, photo)
    