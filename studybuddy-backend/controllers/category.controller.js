const Category = require('../models/Category');

// GET /api/categories  (anyone can view)
const getAllCategories = async (req,res) => {
   try{
    const categories = await Category.getAll();
    res.json(categories);
   }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// POST /api/categories  (admin only)
const createCategory = async (req,res)=>{
    try{
        const {name,description} = req.body;
        if(!name) return res.status(400).json({ message: 'Category name is required' });

        const id=await Category.create({name,description});
        res.status(201).json({ message: 'Category created successfully', category_id: id });

    }catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

module.exports = { getAllCategories, createCategory };