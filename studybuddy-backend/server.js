const express = require('express');
const cors = require('cors');
require('dotenv').config();
require('./config/db');

const app = express();

app.use(cors());
app.use(express.json());   
app.use(express.urlencoded({ extended: true })); // ← add this too


app.get('/',(req,res)=>{
    res.json({ message: 'StudyBuddy API is running' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});

app.use('/api/auth', require('./routes/auth.routes'));
app.use('/api/categories', require('./routes/category.routes'));
app.use('/api/courses', require('./routes/course.routes'));
app.use('/api/enrollments', require('./routes/enrollment.routes'));


