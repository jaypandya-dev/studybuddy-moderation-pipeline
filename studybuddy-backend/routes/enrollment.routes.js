const express = require('express');
const router  = express.Router();
const {
    enrollInCourse, getMyEnrollments,
    getCourseEnrollments, updateProgress, markCompleted
} = require('../controllers/enrollment.controller');
const { protect, authorizeRoles } = require('../middleware/auth.middleware');

router.post('/:course_id',                 protect, authorizeRoles('student'), enrollInCourse);
router.get('/my',                          protect, authorizeRoles('student'), getMyEnrollments);
router.get('/course/:course_id',           protect, authorizeRoles('tutor'),   getCourseEnrollments);
router.put('/:course_id/progress',         protect, authorizeRoles('student'), updateProgress);
router.put('/:course_id/complete',         protect, authorizeRoles('student'), markCompleted);

module.exports = router;