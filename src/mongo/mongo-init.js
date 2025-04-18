db = db.getSiblingDB('company');

// Создаем коллекцию и вставляем заглушку
db.payments.insertOne({
    _id: "init-temp-doc",
    temp: true
});

// Удаляем заглушку
db.payments.deleteOne({ _id: "init-temp-doc" });