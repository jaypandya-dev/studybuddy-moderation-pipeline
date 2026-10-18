const db = require('../config/db');
const bcrypt = require('bcryptjs');

class User{
    
    constructor(data){
        this.user_id      = data.user_id;
        this.first_name   = data.first_name;
        this.last_name    = data.last_name;
        this.email        = data.email;
        this.password_hash = data.password_hash;
        this.role         = data.role;
        this.status       = data.status;
        this.is_verified  = data.is_verified;
        this.created_at   = data.created_at;
    }

    // ── STATIC METHODS ───────────────────────────────────────────

   static async create(data) {
    const salt = await bcrypt.genSalt(10);
    const password_hash = await bcrypt.hash(data.password, salt);

    const [result] = await db.execute(
        `INSERT INTO users 
         (first_name, last_name, email, password_hash, role)
         VALUES (?, ?, ?, ?, 'student')`,
        [data.first_name, data.last_name, data.email, password_hash]
    );
    return result.insertId;
}

    static async getById(user_id) {
        const [rows] = await db.execute(
             'SELECT * FROM users WHERE user_id = ?',
            [user_id]
        );
        return rows.length ? new User(rows[0]) : null;
    }

    static async getByEmail(email) {
        const [rows] = await db.execute(
             'SELECT * FROM users WHERE email = ?',
            [email]
        );
        return rows.length ? new User(rows[0]) : null;
    }

    static async getAll() {
        const [rows] = await db.execute('SELECT * FROM users');
        return rows.map(row => new User(row));
    }

    // ── INSTANCE METHODS ─────────────────────────────────────────

    async verifyPassword(plainpassword){
        return await bcrypt.compare(plainpassword, this.password_hash);
    }

    async updataProfile(dara) {
        await db.execute(
            `UPDATE users SET 
             first_name = ?, last_name = ?, phone = ?, bio = ?, profile_pic = ?
             WHERE user_id = ?`,
            [data.first_name, data.last_name, data.phone, data.bio, data.profile_pic, this.user_id]
        );
    }

    async verifyEmail(){
         await db.execute(
            'UPDATE users SET is_verified = TRUE WHERE user_id = ?',
            [this.user_id]
        );
    }

    async changePassword(newpassword){
        const salt = await bcrypt.genSalt(10);
        const password_hash  = await bcrypt.hash(newpassword, salt);
        await db.execute(
            'UPDATE users SET password_hash = ? WHERE user_id = ?',
            [password_hash, this.user_id]
        );
    }

     async suspend() {
        await db.execute(
            "UPDATE users SET status = 'suspended' WHERE user_id = ?",
            [this.user_id]
        );
    }

    async ban() {
        await db.execute(
            "UPDATE users SET status = 'banned' WHERE user_id = ?",
            [this.user_id]
        );
    } 
    
    async reactivate() {
        await db.execute(
            "UPDATE users SET status = 'active' WHERE user_id = ?",
            [this.user_id]
        );
    }

}

module.exports = User;