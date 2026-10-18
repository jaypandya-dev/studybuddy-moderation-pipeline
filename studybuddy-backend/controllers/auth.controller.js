const User = require('../models/User');
const jwt = require('jsonwebtoken');

// POST /api/auth/register
const register = async (req, res) => {
        console.log('>>> REGISTER hit');  // ← add

    try{
                console.log('Request body:', req.body); // ← add this

        const {first_name, last_name, email, password}=req.body;

        const existing = await User.getByEmail(email);
        if(existing){
            return res.status(400).json({ message: 'User already exists' });
        }

        const user_id = await User.create({first_name, last_name, email, password});
        res.status(201).json({  message: 'Registered successfully' });

    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
}

// POST /api/auth/login
const login = async (req, res) => {
        console.log('>>> LOGIN hit');  // ← add

    try{

        const {email,password} = req.body;

        const user= await User.getByEmail(email);
        if(!user){
            return res.status(400).json({ message: 'Invalid email or password' });
        }
        // Check status
        if (user.status !== 'active') {
            return res.status(403).json({ message: `Account is ${user.status}` });
        }

        // Check password
        const isMatch = await user.verifyPassword(password);
        if (!isMatch) {
            return res.status(400).json({ message: 'Invalid email or password' });
        }

        const token = jwt.sign(
            {user_id: user.user_id, role: user.role},
            process.env.JWT_SECRET,
            {expiresIn: process.env.JWT_EXPIRES_IN}
        );

        res.json({
            message:"Login successfull",
            token,
            user:{
                user_id: user.user_id,
                first_name: user.first_name,
                last_name: user.last_name,
                email: user.email,
                role: user.role
            }
        });


    }
     catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// GET /api/auth/me
const getMe = async (req, res) => {
    res.json({
        user_id:    req.user.user_id,
        first_name: req.user.first_name,
        last_name:  req.user.last_name,
        email:      req.user.email,
        role:       req.user.role,
        status:     req.user.status
    });
};

module.exports = { register, login, getMe };

