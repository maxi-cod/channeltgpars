from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import csv
import asyncio
import os
from dotenv import load_dotenv


load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
channel_id = int(os.getenv('CHANNEL_ID'))

client = TelegramClient('user_session', api_id, api_hash)

async def main():
    await client.start() 
    
    entity = await client.get_entity(channel_id)
    
    seen_ids = set()  
    
    search_queries = (
        [str(i) for i in range(10)] +  
        [chr(i) for i in range(ord('а'), ord('я') + 1)] +  
        [chr(i) for i in range(ord('a'), ord('z') + 1)]  
    )
    total_expected = 2605
    
    with open('channel_users.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Username', 'First Name', 'Last Name'])
        
        for query in search_queries:
            offset = 0
            limit = 200
            
            while True:
                try:
                    participants = await client(GetParticipantsRequest(
                        entity, ChannelParticipantsSearch(query), offset, limit, hash=0
                    ))
                    
                    if not participants.users:
                        break
                        
                    for user in participants.users:
                        if user.id not in seen_ids:
                            seen_ids.add(user.id)
                            writer.writerow([
                                user.id,
                                user.username or '',
                                user.first_name or '',
                                user.last_name or ''
                            ])
                    
                    offset += len(participants.users)
                    print(f'Обработано {offset} участников для запроса "{query}", уникальных: {len(seen_ids)}')
                    
                    if len(seen_ids) >= total_expected:
                        break
                        
                    await asyncio.sleep(2)  
                    
                except Exception as e:
                    print(f'Ошибка для запроса "{query}": {e}. Пауза 10 сек...')
                    await asyncio.sleep(10)
                    break  
            
            if len(seen_ids) >= total_expected:
                break
    
    print(f'Парсинг завершен! Уникальных пользователей: {len(seen_ids)}. Данные сохранены в channel_users.csv')

with client:
    client.loop.run_until_complete(main())