const db = require('../config/db');

class Course{
    constructor(data){
        this.course_id       = data.course_id;
        this.tutor_id        = data.tutor_id;
        this.category_id     = data.category_id;
        this.title           = data.title;
        this.description     = data.description;
        this.what_you_learn  = data.what_you_learn;
        this.course_outcomes = data.course_outcomes;
        this.thumbnail       = data.thumbnail;
        this.duration_hours  = data.duration_hours;
        this.difficulty      = data.difficulty;
        this.language        = data.language;
        this.price           = data.price;
        this.is_published    = data.is_published;
        this.created_at      = data.created_at;
    }

    static async create(data){
        const [result] = await db.execute(
            `INSERT INTO courses 
             (tutor_id, category_id, title, description, what_you_learn, course_outcomes, difficulty, language, price)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
                data.tutor_id,
                data.category_id,
                data.title,
                data.description     || null,
                data.what_you_learn  || null,
                data.course_outcomes || null,
                data.difficulty,
                data.language        || 'English',
                data.price           || 0.00
            ]
        );
        return result.insertId;
    }

    static async getAll(){
         const [rows] = await db.execute(
            `SELECT c.*, u.first_name, u.last_name, cat.name AS category_name
             FROM courses c
             JOIN users u ON c.tutor_id = u.user_id
             JOIN categories cat ON c.category_id = cat.category_id
             WHERE c.is_published = TRUE`
        );
        return rows;
    }

    static async getById(course_id) {
        const [rows] = await db.execute(
            `SELECT c.*, u.first_name, u.last_name, cat.name AS category_name
             FROM courses c
             JOIN users u ON c.tutor_id = u.user_id
             JOIN categories cat ON c.category_id = cat.category_id
             WHERE c.course_id = ?`,
            [course_id]
        );
        return rows.length ? rows[0] : null;
    }

    static async getByTutor(tutor_id) {
        const [rows] = await db.execute(
            `SELECT c.*, cat.name AS category_name
             FROM courses c
             JOIN categories cat ON c.category_id = cat.category_id
             WHERE c.tutor_id = ?
             ORDER BY c.created_at DESC`,
            [tutor_id]
        );
        return rows;
    }

    static async getByCategory(category_id) {
        const [rows] = await db.execute(
            `SELECT c.*, u.first_name, u.last_name
             FROM courses c
             JOIN users u ON c.tutor_id = u.user_id
             WHERE c.category_id = ? AND c.is_published = TRUE`,
            [category_id]
        );
        return rows;
    }

    static async updateDetails(course_id, data) {
        await db.execute(
            `UPDATE courses SET
             title = ?, description = ?, what_you_learn = ?,
             course_outcomes = ?, difficulty = ?, language = ?,
             duration_hours = ?
             WHERE course_id = ?`,
            [
                data.title,
                data.description     || null,
                data.what_you_learn  || null,
                data.course_outcomes || null,
                data.difficulty,
                data.language        || 'English',
                data.duration_hours  || null,
                course_id
            ]
        );
    }

    static async updatePrice(course_id, newPrice) {
        await db.execute(
            'UPDATE courses SET price = ?, price_updated_at = NOW() WHERE course_id = ?',
            [newPrice, course_id]
        );
    }

    static async publish(course_id) {
        await db.execute(
            'UPDATE courses SET is_published = TRUE WHERE course_id = ?',
            [course_id]
        );
    }

    static async unpublish(course_id) {
        await db.execute(
            'UPDATE courses SET is_published = FALSE WHERE course_id = ?',
            [course_id]
        );
    }

    static async delete(course_id) {
        await db.execute(
            'DELETE FROM courses WHERE course_id = ?',
            [course_id]
        );
    }
}

module.exports = Course;
