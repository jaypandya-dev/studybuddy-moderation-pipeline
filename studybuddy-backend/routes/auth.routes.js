const express = require('express');
const router  = express.Router();
const { register, login, getMe } = require('../controllers/auth.controller');
const { protect, authorizeRoles } = require('../middleware/auth.middleware');


router.post('/register', register);
router.post('/login',    login);

router.get('/me', protect, getMe);  // ← protected route




module.exports = router;