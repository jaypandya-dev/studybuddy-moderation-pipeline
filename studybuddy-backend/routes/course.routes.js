const express = require('express');
const router  = express.Router();
const {
    getAllCourses, getCourseById, getMyCourses,
    getCoursesByCategory, createCourse, updateCourse,
    updatePrice, publishCourse, unpublishCourse, deleteCourse
} = require('../controllers/course.controller');
const { protect, authorizeRoles } = require('../middleware/auth.middleware');

router.get('/',                        getAllCourses);
router.get('/tutor/my',                protect, authorizeRoles('tutor'), getMyCourses);
router.get('/category/:category_id',   getCoursesByCategory);
router.get('/:id',                     getCourseById);
router.post('/',                       protect, authorizeRoles('tutor'), createCourse);
router.put('/:id',                     protect, authorizeRoles('tutor'), updateCourse);
router.put('/:id/price',               protect, authorizeRoles('tutor'), updatePrice);
router.put('/:id/publish',             protect, authorizeRoles('tutor'), publishCourse);
router.put('/:id/unpublish',           protect, authorizeRoles('tutor'), unpublishCourse);
router.delete('/:id',                  protect, authorizeRoles('tutor'), deleteCourse);

module.exports = router;