
// Select the database
use("smart_ems_db");


// Find all batch recognition logs
// db.getCollection("batch_recognition_logs")
//     .find({})
//     .sort({ "person_name": 1 })
//     .projection({
//         "confidence_score": 1,
//         "person_name": 1
//     });

db.getCollection("batch_recognition_logs")//.deleteMany({});
    .find({});
