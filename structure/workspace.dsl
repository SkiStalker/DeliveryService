workspace {
    name "Сервис доставки"
    !identifiers hierarchical


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
            notification_service = container "Сервис уведомлений" {
                description "Интегрируется с системой уведомлений для информирования пользователей"
                technology "Java Spring Boot"

                -> notification_system "Отправляет уведомления" "REST"
            }

            payment_registration_service = container "Сервис регистрации платежей" {
                description "Интегрируется с платежной системой для обработки платежей"
                technology "Java Spring Boot"

                -> payment_system "Обрабатывает платежи" "REST"
            }

            database = container "База данных" {
                description "Хранит информацию о пользователях, посылках и доставках"
                technology "PostgreSQL"
            }

            user_management_service = container "Сервис управления пользователями" {
                description "Отвечает за создание и управление данными пользователей"
                technology "Java Spring Boot"

                -> database "Сохраняет и получает данные пользователей" "JDBC"
            }

            parcel_management_service = container "Сервис управления посылками" {
                description "Управляет созданием и отслеживанием посылок"
                technology "Java Spring Boot"

                -> database "Сохраняет и получает данные посылок" "JDBC"
            }


            delivery_management_service = container "Сервис управления доставкой" {
                description "Координирует процесс доставки посылок"
                technology "Java Spring Boot"

                -> database "Сохраняет и получает данные о доставках" "JDBC"
                -> payment_registration_service "Запрашивает обработку платежей" "gRPC"
                -> notification_service "Отправляет уведомления о статусе доставки" "gRPC"
            }

            api_service = container "API-сервис" {
                description "Обрабатывает запросы от веб-приложения и внешних систем"
                technology "Java Spring Boot"

                // Компоненты, представляющие API методы
                create_user_api = component "Создание нового пользователя" {
                    description "API для создания нового пользователя"
                    technology "REST"
                }
                find_user_by_login_api = component "Поиск пользователя по логину" {
                    description "API для поиска пользователя по логину"
                    technology "REST"
                }
                find_user_by_name_surname_api = component "Поиск пользователя по имени и фамилии" {
                    description "API для поиска пользователя по имени и фамилии"
                    technology "REST"
                }
                create_parcel_api = component "Создание посылки" {
                    description "API для создания новой посылки"
                    technology "REST"
                }
                get_user_parcels_api = component "Получение посылок пользователя" {
                    description "API для получения списка посылок пользователя"
                    technology "REST"
                }
                create_delivery_api = component "Создание доставки" {
                    description "API для создания доставки от пользователя к пользователю"
                    technology "REST"
                }
                get_deliveries_by_recipient_api = component "Получение доставок по получателю" {
                    description "API для получения информации о доставках по получателю"
                    technology "REST"
                }
                get_deliveries_by_sender_api = component "Получение доставок по отправителю" {
                    description "API для получения информации о доставках по отправителю"
                    technology "REST"
                }

                -> user_management_service "Управляет данными пользователей" "gRPC"
                -> parcel_management_service "Управляет данными посылок" "gRPC"
                -> delivery_management_service "Управляет процессом доставки" "gRPC"
                
            }

            web_application = container "Веб-приложение" {
                description "Интерфейс для взаимодействия пользователей с системой"
                technology "NextJS"

                -> api_service "Отправляет запросы" "REST"
            }
        }

        // Внешние взаимодействия
        user_sender -> delivery_service.web_application "Создает посылки и инициирует доставку"
        user_receiver -> delivery_service.web_application "Получает информацию о доставке"
        admin -> delivery_service.web_application "Управляет процессами доставки"
        notification_system -> user_receiver "Получает уведомление о новой доставке" "REST"

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

        component delivery_service.api_service {
            include *
            autoLayout
        }

        // Диаграмма динамики для сценария "Создание доставки от пользователя к пользователю"
        dynamic delivery_service {
            title "Создание доставки от пользователя к пользователю"
            user_sender -> delivery_service.web_application "Инициирует создание доставки"
            delivery_service.web_application -> delivery_service.api_service "Отправляет запрос на создание доставки"
            delivery_service.api_service -> delivery_service.parcel_management_service "Создает запись о новой посылке"
            delivery_service.parcel_management_service -> delivery_service.database "Сохраняет данные посылки"
            delivery_service.api_service -> delivery_service.delivery_management_service "Создает запись о доставке"
            delivery_service.delivery_management_service -> delivery_service.database "Сохраняет данные о доставке"
            delivery_service.delivery_management_service -> delivery_service.payment_registration_service "Инициирует процесс оплаты"
            delivery_service.payment_registration_service -> payment_system "Обрабатывает платеж"
            payment_system -> delivery_service.payment_registration_service "Подтверждает успешную оплату"
            delivery_service.payment_registration_service -> delivery_service.delivery_management_service "Сообщает о результате оплаты"
            delivery_service.delivery_management_service -> delivery_service.notification_service "Отправляет уведомление получателю"
            delivery_service.notification_service -> notification_system "Отправляет уведомление о новой доставке"
            notification_system -> user_receiver "Получает уведомление о новой доставке"
        }

        theme default
    }
}
