const db = require('../config/db');

class Category{

    constructor(data){
        this.category_id = data.category_id;
        this.name = data.name;
        this.description = data.description;
        this.created_at = data.created_at;
    }

    static async create(data){
        const [result] = await db.execute(
            'INSERT INTO categories (name, description) VALUES (?, ?)',
            [data.name, data.description]
        );
        return result.insertId;
    }

    static async getAll() {
        const [rows] = await db.execute('SELECT * FROM categories ORDER BY name');
        return rows.map(row => new Category(row));
    }


    static async getById(category_id){
        const [rows] = await db.execute(
             'SELECT * FROM categories WHERE category_id = ?',
            [category_id]
        );
    return rows.length ? new Category(rows[0]) : null;
    }
}

module.exports = Category;
