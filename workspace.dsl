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
                technology "Python GRPC server"

                -> notification_system "Отправляет уведомления" "REST"
            }

            payment_registration_service = container "Сервис регистрации платежей" {
                description "Интегрируется с платежной системой для обработки платежей"
                technology "Python GRPC server"

                -> payment_system "Обрабатывает платежи" "REST"
            }

            database = container "База данных" {
                description "Хранит информацию о пользователях, посылках и доставках"
                technology "PostgreSQL"
            }

            account_management_service = container "Сервис управления сессией пользователя" {
                description "Отвечает за авторизацию, аутентификацию и изменение данных активного пользователя"
                technology "Python GRPC server"

                -> database "Сохраняет и получает данные активного пользователя" "JDBC"
            }

            user_management_service = container "Сервис управления пользователями" {
                description "Отвечает за создание и управление данными пользователей"
                technology "Python GRPC server"

                -> database "Сохраняет и получает данные пользователей" "JDBC"
            }

            parcel_management_service = container "Сервис управления посылками" {
                description "Управляет созданием и отслеживанием посылок"
                technology "Python GRPC server"

                -> database "Сохраняет и получает данные посылок" "JDBC"
            }


            delivery_management_service = container "Сервис управления доставкой" {
                description "Координирует процесс доставки посылок"
                technology "Python GRPC server"

                -> database "Сохраняет и получает данные о доставках" "JDBC"
                -> payment_registration_service "Запрашивает обработку платежей" "gRPC"
                -> notification_service "Отправляет уведомления о статусе доставки" "gRPC"
            }

            api_service = container "API-сервис" {
                description "Обрабатывает запросы от веб-приложения и внешних систем"
                technology "FastAPI"


                token_account_api = component "Получение JWT токенов" {
                    description "API для получения JWT токенов доступа и обновления по логину и паролю"
                    technology "REST"
                    tags "REST, API, POST"
                }

                refresh_account_api = component "Обновление JWT токена доступа" {
                    description "API для обновления JWT токена доступа по JWT токену обновлению"
                    technology "REST"
                    tags "REST, API, POST"
                }

                create_user_api = component "Создание нового пользователя" {
                    description "API для создания нового пользователя"
                    technology "REST"
                    tags "REST, API, POST"
                }
                update_user_api = component "Обновление пользователя" {
                    description "API для обновления данных пользователя"
                    technology "REST"
                    tags "REST, API, POST"
                }
                find_user_by_login_api = component "Поиск пользователя по логину" {
                    description "API для поиска пользователя по логину"
                    technology "REST"
                    tags "REST, API, GET"
                }
                find_user_by_name_surname_api = component "Поиск пользователя по имени и фамилии" {
                    description "API для поиска пользователя по имени и фамилии"
                    technology "REST"
                    tags "REST, API, GET"
                }
                create_parcel_api = component "Создание посылки" {
                    description "API для создания новой посылки"
                    technology "REST"
                    tags "REST, API, POST"
                }
                get_user_parcels_api = component "Получение посылок пользователя" {
                    description "API для получения списка посылок пользователя"
                    technology "REST"
                    tags "REST, API, GET"
                }
                create_delivery_api = component "Создание доставки" {
                    description "API для создания доставки от пользователя к пользователю"
                    technology "REST"
                    tags "REST, API, POST"
                }
                get_deliveries_by_recipient_api = component "Получение доставок по получателю" {
                    description "API для получения информации о доставках по получателю"
                    technology "REST"
                    tags "REST, API, GET"
                }
                get_deliveries_by_sender_api = component "Получение доставок по отправителю" {
                    description "API для получения информации о доставках по отправителю"
                    technology "REST"
                    tags "REST, API, GET"
                }

                -> user_management_service "Управляет данными пользователей" "gRPC"
                -> parcel_management_service "Управляет данными посылок" "gRPC"
                -> delivery_management_service "Управляет процессом доставки" "gRPC"
                -> account_management_service "Управляет авторизацией, аутентификацией и данными активного пользователя" "gRPC"
                
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



        deploymentEnvironment "PROD" {
            deploymentNode "DMZ" {
                deploymentNode "api_gateway" {
                    containerInstance delivery_service.api_service
                }
            }

            deploymentNode "PROTECTED" {
                deploymentNode "docker-compose" {

                    deploymentNode "user" {
                        containerInstance delivery_service.user_management_service
                    }
                    deploymentNode "db" {
                        containerInstance delivery_service.database
                    }
                    
                    deploymentNode "account" {
                        containerInstance delivery_service.account_management_service
                    }
                }

            }
        }
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
            user_sender -> delivery_service.web_application "Пользователь авторизуется"
            delivery_service.web_application -> delivery_service.api_service "Отправляются данные для авторизации"
            delivery_service.api_service -> delivery_service.account_management_service "Отправляются данные для авторизации"
            delivery_service.account_management_service -> delivery_service.database "Производится запрос данных для указанного пользователя"
            delivery_service.database -> delivery_service.account_management_service "Возвращаются данные для указанного пользователя"
            delivery_service.account_management_service -> delivery_service.api_service "Отправляются результаты авторизации"
            delivery_service.api_service -> delivery_service.web_application "Отправляются результаты авторизации"
            delivery_service.web_application -> user_sender "Пользователю отображаются результаты его авторизации"
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
