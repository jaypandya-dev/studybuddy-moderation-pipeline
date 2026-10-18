const Course = require('../models/Course');

// GET /api/courses — public, all published courses
const getAllCourses = async (req, res) => {
    try {
        const courses = await Course.getAll();
        res.json(courses);
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// GET /api/courses/:id — public
const getCourseById = async (req, res) => {
    try{
        const course = await Course.getById(req.params.id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        res.json(course);
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
}

// GET /api/courses/tutor/my — tutor sees their own courses
const getMyCourses = async (req, res) => {
    try{
        const courses = await Course.getByTutor(req.user.user_id);
        res.json(courses);
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
}

// GET /api/courses/category/:category_id — public
const getCoursesByCategory = async (req, res) => {
    try{
        const courses = await Course.getByCategory(req.params.category_id);
        res.json(courses);
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// POST /api/courses — tutor only
const createCourse = async (req, res) => {
    try{
        const data={...req.body,tutor_id:req.user.user_id};
        
        if(!data.title || !data.category_id || !data.difficulty){
            return res.status(400).json({ message: 'title, category_id and difficulty are required' });
        }
        const id = await Course.create(data);
        res.status(201).json({ message: 'Course created successfully', course_id: id });
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// PUT /api/courses/:id — tutor only (must own the course)
const updateCourse = async (req, res) => {
    try{
        const course = await Course.getById(req.params.id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        if(course.tutor_id !== req.user.user_id) return
         res.status(403).json({ message: 'Not your course' });

        await Course.updateDetails(req.params.id, req.body);
        res.json({ message: 'Course updated successfully' });
    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// PUT /api/courses/:id/price — tutor only
const updatePrice = async (req,res)=>{
    try{
        const course = await Course.getById(req.params.id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        if(course.tutor_id != req.user.user_id) return res.status(403).json({ message: 'Not your course' });    

        const { price } = req.body;
        if(price === undefined) return res.status(400).json({ message: 'price is required' });

        await Course.updatePrice(req.params.id,price);
        res.json({ message: 'Price updated successfully' });

    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// PUT /api/courses/:id/publish — tutor only
const publishCourse = async (req, res) => {
    try{
        const course = await Course.getById(req.params.id);
        if(!course) return res.status(404).json({ message: 'Course not found' });

        if(course.tutor_id !== req.user.user_id) return res.status(403).json({ message: 'Not your course' });

        await Course.publish(req.params.id);
        res.json({ message: 'Course published successfully' });
    }  catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// PUT /api/courses/:id/unpublish — tutor only
const unpublishCourse = async (req, res) => {
    try{
        const course = await Course.getById(req.params.id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        if(course.tutor_id !== req.user.user_id) return res.status(403).json({ message: 'Not your course' });

        await Course.unpublish(req.params.id);
        res.json({ message: 'Course unpublished'});
    }
    catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// DELETE /api/courses/:id — tutor only
const deleteCourse = async (req, res) => {
    try{
        const course = await Course.getById(req.params.id);
        if(!course) return res.status(404).json({ message: 'Course not found' });
        if(course.tutor_id !== req.user.user_id) return res.status(403).json({ message: 'Not your course' });

        await Course.delete(req.params.id);
        res.json({ message: 'Course deleted'});
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};


module.exports = {
    getAllCourses, getCourseById, getMyCourses,
    getCoursesByCategory, createCourse, updateCourse,
    updatePrice, publishCourse, unpublishCourse, deleteCourse
};