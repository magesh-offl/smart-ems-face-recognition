
// Select the database
use("face_recognition_db");


// Find all batch recognition logs
db.getCollection("batch_recognition_logs")
    .find({})
    .sort({ "person_name": 1 })
    .projection({
        "confidence_score": 1,
        "person_name": 1
    });


