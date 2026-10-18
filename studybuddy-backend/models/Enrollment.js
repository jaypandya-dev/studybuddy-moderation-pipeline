const db = require('../config/db');

class Enrollment{

    constructor(data){
        this.enrollment_id   = data.enrollment_id;
        this.student_id      = data.student_id;
        this.course_id       = data.course_id;
        this.status          = data.status;
        this.progress        = data.progress;
        this.enrolled_at     = data.enrolled_at;
        this.completed_at    = data.completed_at;
    }

    static async enroll(student_id,course_id){
        const [result] = await db.execute(
             `INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)`,
            [student_id, course_id]
        );
        return result.insertId;
    }

    static async getByStudent(student_id){
        const [rows] = await db.execute(
            `SELECT e.*, c.title, c.thumbnail, c.difficulty,
                    u.first_name, u.last_name
             FROM enrollments e
             JOIN courses c ON e.course_id = c.course_id
             JOIN users u ON c.tutor_id = u.user_id
             WHERE e.student_id = ?
             ORDER BY e.enrolled_at DESC`,
            [student_id]
        );
        return rows;
    }

    static async getByCourse(course_id){
        const [rows] = await db.execute(
             `SELECT e.*, u.first_name, u.last_name, u.email
             FROM enrollments e
             JOIN users u ON e.student_id = u.user_id
             WHERE e.course_id = ?
             ORDER BY e.enrolled_at DESC`,
            [course_id]
        );
        return rows;
    }

    static async isEnrolled(student_id,course_id){
        const [row] = await db.execute(
            `SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?`,
            [student_id, course_id]
        );
        return row.length > 0;
    }

    static async updateProgress(student_id,course_id,progress){
        await db.execute(
            `UPDATE enrollments SET progress = ? WHERE student_id = ? AND course_id = ?`,
            [progress, student_id, course_id]
        );
    }

    static async markCompleted(student_id,course_id){
        await db.execute(
            `UPDATE enrollments 
             SET status = 'completed', progress = 100, completed_at = NOW()
             WHERE student_id = ? AND course_id = ?`,
            [student_id, course_id]
        );
    }
}

module.exports = Enrollment;