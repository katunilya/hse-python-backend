## Requirements

- Python => 3.7 
   ```bash
   cd chat_app
   pip install -r requirements.tx

## Launch
```bash
# Запуск сервера
uvicorn main:app --reload

# Запуск клиента (создаем нужное количество клиентов в разных терминалах)
python client.py

