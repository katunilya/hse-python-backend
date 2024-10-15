import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 }, // Поднимаем нагрузку до 50 пользователей за 2 минуты
    { duration: '5m', target: 100 }, // Поддерживаем 100 пользователей в течение 5 минут
    { duration: '2m', target: 0 },  // Уменьшаем нагрузку до 0
  ],
};

export default function () {
  let res = http.get('http://shop_api:8000/cart'); //
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
