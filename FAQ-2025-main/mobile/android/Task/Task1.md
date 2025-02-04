#  Задача 1 | Рекламный баннер – получение данных

[⬅️ назад](../README.md)

## ТЗ

Необходимо реализовать логику получения данных для отображения рекламного баннера.

### Запрос API данных

Метод: `BannerRemoteDataSource.getBanner()`

Результат запроса должен представляться моделью `BannerInfo`, создаваемой из JSON, получаемого из `JsonProvider.bannerInfoJson`

### Репозиторий

Метод: `BannerRepository.getBannerInfo()`

Результатом метода должен быть объект `BannerInfo`, полученный из `BannerRemoteDataSource.getBanner()`

## Ожидаемое решение

* Необходимо реализовать `BannerRemoteDataSourceImpl`, который производит запрос на получение данных из сети (`JsonProvider`)
* Внутри `BannerRemoteDataSourceImpl` должна быть логика парсинга JSON в модель `BannerInfo`
* `BannerRemoteDataSourceImpl` должен реализовывать интерфейс `BannerRemoteDataSource`.
* Необходимо реализовать `BannerRepositoryImpl`, который возвращает данные из `BannerRemoteDataSource.getBanner()`
* `BannerRepositoryImpl` должен реализовывать интерфейс `BannerRepository`.
