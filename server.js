import express from 'express';
import fs from 'fs';
import path from 'path';
import multer from 'multer';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;
const DB_FILE = path.join(__dirname, 'database.json');
const UPLOADS_DIR = path.join(__dirname, 'uploads');

// Uploads papkasini tekshirish
if (!fs.existsSync(UPLOADS_DIR)) {
    fs.mkdirSync(UPLOADS_DIR);
}
if (!fs.existsSync(DB_FILE)) {
    fs.writeFileSync(DB_FILE, '[]', 'utf8');
}

// Multer konfiguratsiyasi
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOADS_DIR),
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        cb(null, Date.now() + '-' + Math.round(Math.random() * 1e6) + ext);
    }
});
const upload = multer({
    storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
    fileFilter: (req, file, cb) => {
        if (file.mimetype.startsWith('image/')) cb(null, true);
        else cb(new Error('Faqat rasm fayllar qabul qilinadi'));
    }
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(__dirname));
app.use('/uploads', express.static(UPLOADS_DIR));

// ==========================================
// RASM YUKLASH API
// ==========================================

// Bitta rasm yuklash
app.post('/api/upload', upload.single('image'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'Rasm tanlanmadi' });
    res.json({ url: '/uploads/' + req.file.filename });
});

// Rasmni o'chirish
app.delete('/api/upload/:filename', (req, res) => {
    const filePath = path.join(UPLOADS_DIR, req.params.filename);
    if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
    }
    res.json({ success: true });
});

// ==========================================
// MAHSULOTLAR API
// ==========================================

app.get('/api/products', (req, res) => {
    try {
        const data = fs.readFileSync(DB_FILE, 'utf8');
        res.json(JSON.parse(data || '[]'));
    } catch (e) {
        res.json([]);
    }
});

app.post('/api/products', (req, res) => {
    try {
        const data = fs.readFileSync(DB_FILE, 'utf8');
        const products = JSON.parse(data || '[]');
        const images = req.body.images || [];
        const newProduct = {
            id:       Date.now(),
            title:    req.body.title    || 'Nomsiz',
            price:    Number(req.body.price) || 0,
            images:   Array.isArray(images) ? images : [images],
            fabric:   req.body.fabric   || '100% Paxta',
            sizes:    req.body.sizes    || 'M, L, XL',
            category: req.body.category || 'Boshqa',
            stock:    Number(req.body.stock) ?? 10
        };
        products.push(newProduct);
        fs.writeFileSync(DB_FILE, JSON.stringify(products, null, 2), 'utf8');
        res.status(201).json(newProduct);
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.put('/api/products/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const data = fs.readFileSync(DB_FILE, 'utf8');
        let products = JSON.parse(data || '[]');
        products = products.map(p => {
            if (p.id === id) {
                const images = req.body.images;
                return {
                    ...p,
                    title:    req.body.title    !== undefined ? req.body.title    : p.title,
                    price:    req.body.price    !== undefined ? Number(req.body.price) : p.price,
                    images:   images            !== undefined ? (Array.isArray(images) ? images : [images]) : p.images,
                    fabric:   req.body.fabric   !== undefined ? req.body.fabric   : p.fabric,
                    sizes:    req.body.sizes    !== undefined ? req.body.sizes    : p.sizes,
                    category: req.body.category !== undefined ? req.body.category : p.category,
                    stock:    req.body.stock    !== undefined ? Number(req.body.stock) : p.stock
                };
            }
            return p;
        });
        fs.writeFileSync(DB_FILE, JSON.stringify(products, null, 2), 'utf8');
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.delete('/api/products/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const data = fs.readFileSync(DB_FILE, 'utf8');
        let products = JSON.parse(data || '[]');
        products = products.filter(p => p.id !== id);
        fs.writeFileSync(DB_FILE, JSON.stringify(products, null, 2), 'utf8');
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server muvaffaqiyatli yoqildi: http://localhost:${PORT}`);
});
