# K1rkaSBOT
Twitch чат бот, который запускается и работает на компьютере пользователя. Предоставляет набор развлекательных команд для зрителей и вспомогательных для модераторов.

## Команды для зрителей:
* **!привет** и подобные шаблонные команды выводят в чат заранее заготовленную фразу;
* **!время** - отправляет в чат время компьютера, на котором запущен бот (предполагается, что это время стримера);
* **!слово** - мини-игра Wordly для чата;
* **!копать** - отправит в чат случайную фразу из тематического списка;
* **!задача** - отправит в чат случайный математический пример для решения;
* **!розыгрыш +** - записывает зрителя на розыгрыш, если тот запущен;
* **!кубик** - выводит в чат случайное число от 1 до 100 с возможностью указать верхний предел. Предусмотренны отдельные реакции на "критические" провал и успех;
* **!рулетка** - мини-игра "русская рулетка". В случае поражения отстраняет игрока на 1 минуту;
* **!бомба** - мини-игра, где нужно угадать правильный цвет провода. В случае поражения отстраняет игрока на 1 минуту;
* **!реклама** - через ссылку в чате рекламирует выбранный стримером ресурс;
* **!рейтинг** - выводит в чат топ 10 пользователей по количеству сообщений;
* **!клип <ссылка на ютуб>** - запускает в мини-проигрывателе видео из ссылки (предположительно - музыку). Для отображения на стриме нужно захватить проигрыватель в OBS.

## Команды для модераторов:
* **!копать add <фраза>** - добавляет новую фразу в список;
* **!копать del <фраза>** - удаляет фразу из списка;
* **!розыгрыш начало** - открывает возможность зрителям записаться на розыгрыш;
* **!розыгрыш конец** - закрывает возможность записи на розыгрыш и определяет случайного победителя;
* **!бан <@никнейм0> <@никнейм1> ...** - банит несколько пользователей сразу;
* **!мут <время в секундах> <@никнейм0> <@никнейм1> ...** - остраняет несколько пользователей сразу на указанное время (не более недели);

## Дополнительный функционал:
* Раз в 25 минут сообщает об количестве зрителей на трансляции в данный момент или присылает ссылку из команды **!реклама**;
* Проверяет сообщения зрителей на бан-ворды из чёрного списка. В случае их нахождения отстраняет пользователя на 30 минут. Предусмотрена замена символов в бан-вордах. Например, когда I заменена на 1, у (рус) на y (eng) и подобные. Стример может добавлять новые бан-ворды через консоль в приложении бота;
* Считает пользователей, которые часто используют бан-ворды. В случае их появления в чате, бот сообщит об этом в консоль;
* Отслеживает начало и конец трансляции. Сообщает о старте и конце в чат.

## Интерфейс программы:
Интерфейс содержит поле для ввода никнейма канала, на котором нужно запустить бота. Бот начнёт работу после нажатия кнопки **запустить** и прекратит сразу после закрытия программы. Так же имеется консоль, которая выводит все возможные ошибки. 
Для стримера предусмотренно несколько команд в консоли:
* **банворд добавить <слово>** - добавляет слово в чёрный список для автомодерации;
* **банворд удалить <слово>** - удаляет слово из чёрного списка;
* **банворд список** - выводит список всех бан-вордов;
* **плохиши** - выводит список зрителей, наиболее часто использующие бан-ворды;

###### Консольные команды не выводят ничего в Twitch-чат, т.к. могут содержать запрещённый платформой контент.
Так же вместе с программой для запуска бота отдельно открывается окно с Youtube-проигрывателем для удобного захвата через OBS.
