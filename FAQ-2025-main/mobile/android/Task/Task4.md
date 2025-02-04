# Задача 4 | Товарная витрина – получение данных

[⬅️ назад](../README.md)

## ТЗ

Необходмио реализовать логику получения данных для отображения витрины товаров.


### Запрос API данных - Бонусы

Метод: `BonusesRemoteDataSource.getAllBonuses()`

Результат запроса должен представляться списком моделей `BonusInfo`, создаваемых из JSON,
получаемого из `JsonProvider.allBonusesJson`

Опциональные поля
- available_due_to
- promotion_extra


### Запрос API данных - Товары

Метод: `GoodsRemoteDataSource.getAllGoods()`

Результат запроса должен представляться списком моделей `GoodInfo`, создаваемых из JSON,
получаемого из `JsonProvider.allGoodsJson`.

Опциональные поля
- rating
- bonus_ids
- is_new


### Запрос API данных - Информация о пользователе

Метод: `UserRemoteDataSource.getUserInfo()`

Результат запроса должен представляться моделью `UserInfo`, создаваемой из JSON,
получаемого из `JsonProvider.userInfo`.

---

### Кэширование данных - Бонусы

Метод: `BonusesLocalDataSource.cacheBonuses(bonuses: List<BonusInfo>)`

Результатом выполнения метода должно быть сохранение переданного списка объектов `BonusInfo`, 
полученного из `BonusesRemoteDataSource.getAllBonuses()`.

Метод: `BonusesLocalDataSource.getCachedBonuses()`

Результатом метода должен быть список объектов `BonusInfo`, сохраненных ранее с помощью 
метода `BonusesLocalDataSource.cacheBonuses(bonuses: List<BonusInfo>)`. 
Если закэшированных данных нет, то нужно отдавать пустой список.


### Кэширование данных - Товары

Метод: `GoodsLocalDataSource.cacheGoods(goods: List<GoodInfo>)`

Результатом выполнения метода должно быть сохранение переданного списка объектов `GoodInfo`,
полученного из `GoodsRemoteDataSource.getAllGoods()`.

Метод: `GoodsLocalDataSource.getCachedGoods()`

Результатом метода должен быть список объектов `GoodInfo`, сохраненных ранее с помощью
метода `GoodsLocalDataSource.cacheGoods(goods: List<GoodInfo>)`.
Если закэшированных данных нет, то нужно отдавать пустой список.

---

### Репозиторий - Бонусы

Метод: `BonusesRepository.getAllBonuses()`

Результатом метода должен быть список объектов `BonusInfo`. 
Необходимо получить данные из кэша `BonusesLocalDataSource.getCachedBonuses()`, 
если спиоск пуст, то загружаем данные из сети с помошью 
метода `BonusesRemoteDataSource.getAllBonuses()`, а затем 
кэшируем `BonusesLocalDataSource.cacheBonuses(bonuses: List<BonusInfo>)`.
Если список из кэша не пустой, то необходимо возвращать его в качестве результата.


### Репозиторий - Товары

Метод: `GoodsRepository.getAllGoods()`

Результатом метода должен быть список объектов `GoodInfo`.
Необходимо получить данные из кэша `GoodsLocalDataSource.getCachedGoods()`,
если спиоск пуст, то загружаем данные из сети с помошью
метода `GoodsRemoteDataSource.getAllGoods()`, а затем
кэшируем `GoodsLocalDataSource.cacheGoods(goods: List<GoodInfo>)`.
Если список из кэша не пустой, то необходимо возвращать его в качестве результата.


### Репозиторий - Информация о пользователе

Метод: `UserRepository.getUserInfo()`

Результатом метода должен быть объект `UserInfo`, полученный из `UserRemoteDataSource.getUserInfo()`.

---

## Ожидаемое решение

* Необходимо реализовать `BonusesRemoteDataSourceImpl`, `GoodsRemoteDataSourceImpl`,
  `UserRemoteDataSourceImpl`, которые производят запрос на получение данных из сети (`JsonProvider`).
* Внутри `BonusesRemoteDataSourceImpl` должна быть логика парсинга JSON в модель `BonusInfo`.
* Внутри `GoodsRemoteDataSourceImpl` должна быть логика парсинга JSON в модель `GoodInfo`.
* Внутри `UserRemoteDataSourceImpl` должна быть логика парсинга JSON в модель `UserInfo`.
* Необходимо реализовать `BonusesLocalDataSourceImpl`, `GoodsLocalDataSourceImpl`,
  которые кэшируют данные (достаточно будет хранить их в переменной).
* Необходимо реализовать `BonusesRepository`, который возвращает данные из 
  `BonusesLocalDataSource.getCachedBonuses()` или `BonusesRemoteDataSource.getAllBonuses()`.
* Необходимо реализовать `GoodsRepository`, который возвращает данные из
  `GoodsLocalDataSource.getCachedGoods()` или `GoodsRemoteDataSource.getAllGoods()()`.
* Необходимо реализовать `UserRepository`, который возвращает данные из `UserRemoteDataSource.getUserInfo()`.
