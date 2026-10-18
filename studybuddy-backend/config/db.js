const mysql2= require('mysql2');
require('dotenv').config();

const pool =  mysql2.createPool({
    host:process.env.DB_HOST,
    user:process.env.DB_USER,
    password:process.env.DB_PASSWORD,
    database:process.env.DB_NAME,  
    waitForConnections:true,
    connectionLimit:10,
    
});

const db = pool.promise();

db.getConnection()
    .then(connection => {
        console.log('DB is connected');
        connection.release();
    })
    .catch(err => {
        console.error('DB is not connected');
    });

module.exports = db;