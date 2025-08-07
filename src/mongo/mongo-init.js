db = db.getSiblingDB('company');

db.payments.insertOne({
    _id: "init-temp-doc",
    temp: true
});

db.payments.deleteOne({ _id: "init-temp-doc" });