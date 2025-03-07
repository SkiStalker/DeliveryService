workspace {

    model {
        // Пользователи
        user_sender = person "Отправитель" {
            description "Пользователь, отправляющий посылку"
        }
        user_receiver = person "Получатель" {
            description "Пользователь, получающий посылку"
        }
        admin = person "Администратор" {
            description "Сотрудник, управляющий процессами доставки"
        }

        // Внешние системы
        payment_system = softwareSystem "Платежная система" {
            description "Обрабатывает платежи за услуги доставки"
        }
        notification_system = softwareSystem "Система уведомлений" {
            description "Отправляет уведомления о статусе доставки"
        }

        // Основная система
        delivery_service = softwareSystem "Сервис доставки" {
            description "Обеспечивает управление процессом доставки посылок"

            // Контейнеры
            web_application = container "Веб-приложение" {
                description "Интерфейс для взаимодействия пользователей с системой"
                technology "NextJS"
            }
            api_service = container "API-сервис" {
                description "Обрабатывает запросы от веб-приложения и внешних систем"
                technology "Java Spring Boot"
            }
            user_management_service = container "Сервис управления пользователями" {
                description "Отвечает за создание и управление данными пользователей"
                technology "Java Spring Boot"
            }
            parcel_management_service = container "Сервис управления посылками" {
                description "Управляет созданием и отслеживанием посылок"
                technology "Java Spring Boot"
            }
            delivery_management_service = container "Сервис управления доставкой" {
                description "Координирует процесс доставки посылок"
                technology "Java Spring Boot"
            }
            payment_registration_service = container "Сервис регистрации платежей" {
                description "Интегрируется с платежной системой для обработки платежей"
                technology "Java Spring Boot"
            }
            notification_service = container "Сервис уведомлений" {
                description "Интегрируется с системой уведомлений для информирования пользователей"
                technology "Java Spring Boot"
            }
            database = container "База данных" {
                description "Хранит информацию о пользователях, посылках и доставках"
                technology "PostgreSQL"
            }
        }

        // Взаимодействия
        user_sender -> web_application "Создает посылки и инициирует доставку"
        user_receiver -> web_application "Получает информацию о доставке"
        admin -> web_application "Управляет процессами доставки"
        web_application -> api_service "Отправляет запросы" technology "HTTPS"
        api_service -> user_management_service "Управляет данными пользователей" technology "gRPC"
        api_service -> parcel_management_service "Управляет данными посылок" technology "gRPC"
        api_service -> delivery_management_service "Управляет процессом доставки" technology "gRPC"
        user_management_service -> database "Сохраняет и получает данные пользователей" technology "JDBC"
        parcel_management_service -> database "Сохраняет и получает данные посылок" technology "JDBC"
        delivery_management_service -> database "Сохраняет и получает данные о доставках" technology "JDBC"
        delivery_management_service -> payment_registration_service "Запрашивает обработку платежей" technology "gRPC"
        payment_registration_service -> payment_system "Обрабатывает платежи" technology "HTTPS"
        delivery_management_service -> notification_service "Отправляет уведомления о статусе доставки" technology "gRPC"
        notification_service -> notification_system "Отправляет уведомления" technology "HTTPS"
        notification_system -> user_receiver "Получает уведомление о новой доставке" technology "HTTPS"
    }

    views {
        // Диаграмма контекста системы
        systemContext delivery_service {
            include *
        }

        // Диаграмма контейнеров
        container delivery_service {
            include *
        }

        // Диаграмма динамики для сценария "Создание доставки от пользователя к пользователю"
        dynamic delivery_service {
            title "Создание доставки от пользователя к пользователю"
            user_sender -> web_application "Инициирует создание доставки"
            web_application -> api_service "Отправляет запрос на создание доставки"
            api_service -> parcel_management_service "Создает запись о новой посылке"
            parcel_management_service -> database "Сохраняет данные посылки"
            api_service -> delivery_management_service "Создает запись о доставке"
            delivery_management_service -> database "Сохраняет данные о доставке"
            delivery_management_service -> payment_registration_service "Инициирует процесс оплаты"
            payment_registration_service -> payment_system "Обрабатывает платеж"
            payment_system -> payment_registration_service "Подтверждает успешную оплату"
            payment_registration_service -> delivery_management_service "Сообщает о результате оплаты"
            delivery_management_service -> notification_service "Отправляет уведомление получателю"
            notification_service -> notification_system "Отправляет уведомление о новой доставке"
            notification_system -> user_receiver "Получает уведомление о новой доставке"
        }

        theme default
    }
}
