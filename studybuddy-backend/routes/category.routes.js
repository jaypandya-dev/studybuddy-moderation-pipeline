const express    = require('express');
const router     = express.Router();
const { getAllCategories, createCategory } = require('../controllers/category.controller');
const { protect, authorizeRoles } = require('../middleware/auth.middleware');

router.get('/',  getAllCategories);                             // public
router.post('/', protect, authorizeRoles('admin'), createCategory); // admin only

module.exports = router;