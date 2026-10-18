const Enrollment = require('../models/Enrollment');
const Course     = require('../models/Course');

// POST /api/enrollments/:course_id — student enrolls
const enrollInCourse = async (req, res) => {
    try{
          
        const course = await Course.getById(req.params.course_id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        if(!course.is_published) return res.status(400).json({ message: 'Course is not published' });   

        const alreadyEnrolled = await Enrollment.isEnrolled(req.user.user_id,req.params.course_id);
        if(alreadyEnrolled) return res.status(400).json({ message: 'You are already enrolled in this course' });   

        const enrollment_id = await Enrollment.enroll(req.user.user_id, req.params.course_id);
        res.json({ message: 'Enrolled successfully', enrollment_id: enrollment_id });   
    }    catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// GET /api/enrollments/my — student sees their courses
const getMyEnrollments = async (req, res) => {
    try{
        const enrollments= await Enrollment.getByStudent(req.user.user_id);
        res.json(enrollments);
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
}

// GET /api/enrollments/course/:course_id — tutor sees who enrolled
const getCourseEnrollments = async (req, res) => {
    try{
        const course = await Course.getById(req.params.course_id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        if(course.tutor_id !== req.user.user_id) return res.status(403).json({ message: 'Not your course' });

        const enrollments= await Enrollment.getByCourse(req.params.course_id);
        res.json(enrollments);
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
}

// PUT /api/enrollments/:course_id/progress — student updates progress
const updateProgress = async (req, res) => {
    try{
        const { progress } = req.body;
        if(progress === undefined || progress < 0 || progress > 100){
            return res.status(404).json({message:"progress must be betweeen 0 and 100"});
        }
        
        const enrolled = await Enrollment.isEnrolled(req.user.user_id, req.params.course_id);
        if(!enrolled) return res.status(404).json({ message: 'You are not enrolled in this course' });
        await Enrollment.updateProgress(req.user.user_id, req.params.course_id, progress);
        res.json({ message: 'Progress updated successfully' }); 
    }  
    catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// PUT /api/enrollments/:course_id/complete — student marks complete
const markCompleted = async (req, res) => {
  try{
    const enrolled = await Enrollment.isEnrolled(req.user.user_id, req.params.course_id);
    if(!enrolled) return res.status(404).json({ message: 'You are not enrolled in this course' });
    await Enrollment.markCompleted(req.user.user_id, req.params.course_id);
    res.json({ message: 'Completed successfully' }); 
  }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
  };

module.exports = { enrollInCourse, getMyEnrollments, getCourseEnrollments, updateProgress, markCompleted };