import os
import json
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import sys

PORT = 3000
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')

# Ensure database.json exists
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        f.write('[]')

# HTML content to serve at /
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIGOR | Erkaklar kiyimi do'koni</title>
    <script>
        window.onerror = function(message, source, lineno, colno, error) {
            var div = document.createElement('div');
            div.style.color = 'red';
            div.style.padding = '20px';
            div.style.background = '#fee';
            div.style.border = '1px solid red';
            div.style.margin = '20px';
            div.style.fontFamily = 'monospace';
            div.style.whiteSpace = 'pre-wrap';
            div.innerHTML = '<h3>JavaScript xatoligi:</h3>' + 
                            '<p><b>Xabar:</b> ' + message + '</p>' +
                            '<p><b>Manba:</b> ' + source + '</p>' +
                            '<p><b>Qator:</b> ' + lineno + ':' + colno + '</p>';
            if (document.body) {
                document.body.appendChild(div);
            } else {
                window.addEventListener('DOMContentLoaded', function() {
                    document.body.appendChild(div);
                });
            }
            return false;
        };
    </script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone@7/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900">
    <div id="root"></div>

    <script type="text/babel">
        function App() {
            const [products, setProducts] = React.useState([]);
            const [isAdmin, setIsAdmin] = React.useState(false);
            
            const [showSplash, setShowSplash] = React.useState(true);
            
            // Form states
            const [title, setTitle] = React.useState('');
            const [price, setPrice] = React.useState('');
            const [image, setImage] = React.useState('');
            const [fabric, setFabric] = React.useState('100% Paxta (Xlopok)');
            const [sizes, setSizes] = React.useState('M, L, XL, XXL');
            const [editingId, setEditingId] = React.useState(null);

            React.useEffect(() => {
                fetchProducts();
                const timer = setTimeout(() => {
                    setShowSplash(false);
                }, 2000);
                return () => clearTimeout(timer);
            }, []);

            const fetchProducts = () => {
                fetch('/api/products').then(res => res.json()).then(data => setProducts(data));
            };

            const handleFileChange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        setImage(reader.result);
                    };
                    reader.readAsDataURL(file);
                }
            };

            const handleSubmit = (e) => {
                e.preventDefault();
                const productData = { title, price: Number(price), image, fabric, sizes };

                if (editingId) {
                    fetch('/api/products/' + editingId, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(productData)
                    }).then(() => { setEditingId(null); clearForm(); fetchProducts(); });
                } else {
                    fetch('/api/products', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(productData)
                    }).then(() => { clearForm(); fetchProducts(); });
                }
            };

            const startEdit = (p) => {
                setEditingId(p.id); setTitle(p.title); setPrice(p.price); setImage(p.image); setFabric(p.fabric); setSizes(p.sizes);
            };

            const formatPrice = (price) => {
                const num = Number(price);
                const actual = num < 10000 ? num * 1000 : num;
                return actual.toLocaleString() + " so'm";
            };

            const clearForm = () => {
                setTitle(''); setPrice(''); setImage(''); setFabric('100% Paxta (Xlopok)'); setSizes('M, L, XL, XXL');
            };

            const openTelegram = (product) => {
                const message = 'Salom VIGOR, men shu kiyimni sotib olmoqchiman:\\n\\n' + product.title + '\\nNarxi: ' + formatPrice(product.price) + '\\nMato: ' + product.fabric + '\\nRazmer: ' + product.sizes;
                window.open('https://t.me/SizningTelegramUsernamingiz?text=' + encodeURIComponent(message), '_blank');
            };

            return (
                <div className="min-h-screen flex flex-col relative">
                    {/* Splash Screen */}
                    <div className={`fixed inset-0 bg-black flex flex-col items-center justify-center z-[9999] transition-all duration-1000 ${showSplash ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
                        <img src="/logo.jpg" className="w-64 h-64 object-cover rounded-full border-4 border-yellow-500 shadow-2xl animate-pulse" alt="VIGOR Logo" />
                        <h2 className="text-yellow-500 text-3xl font-extrabold tracking-widest mt-6 animate-bounce">V I G O R</h2>
                    </div>

                    <header className="bg-black text-white p-4 sticky top-0 z-50 shadow-md flex justify-between items-center">
                        <h1 className="text-2xl font-bold tracking-widest text-yellow-500">V I G O R</h1>
                        <button onClick={() => setIsAdmin(!isAdmin)} className="bg-yellow-600 hover:bg-yellow-500 text-white px-4 py-2 rounded text-sm font-semibold transition">
                            {isAdmin ? "Do'konni ko'rish" : "Admin Panel"}
                        </button>
                    </header>

                    <main className="flex-grow container mx-auto px-4 py-8">
                        {isAdmin ? (
                            <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-lg">
                                <h2 className="text-xl font-bold mb-4 text-center text-gray-800">
                                    {editingId ? "Kiyim Narxini O'zgartirish" : "Yangi Kiyim Qo'shish"}
                                </h2>
                                <form onSubmit={handleSubmit} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium">Kiyim nomi</label>
                                        <input type="text" value={title} onChange={e => setTitle(e.target.value)} className="w-full border p-2 rounded" required />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium">Narxi (ming so'mda, masalan: 229 kiritilsa 229 000 so'm bo'ladi)</label>
                                        <input type="number" value={price} onChange={e => setPrice(e.target.value)} className="w-full border p-2 rounded" required />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium">Tovarni rasmini yuklash</label>
                                        <input type="file" accept="image/*" onChange={handleFileChange} className="w-full border p-2 rounded" />
                                        {image && (
                                            <div className="mt-2 flex items-center space-x-2">
                                                <img src={image} alt="Yuklangan rasm" className="h-16 w-16 object-cover rounded border" />
                                                <button type="button" onClick={() => setImage('')} className="text-red-600 text-xs font-semibold hover:underline">O'chirish</button>
                                            </div>
                                        )}
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium">Mato tarkibi</label>
                                        <input type="text" value={fabric} onChange={e => setFabric(e.target.value)} className="w-full border p-2 rounded" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium">Mavjud Razmerlar</label>
                                        <input type="text" value={sizes} onChange={e => setSizes(e.target.value)} className="w-full border p-2 rounded" />
                                    </div>
                                    <button type="submit" className="w-full bg-green-600 text-white p-3 rounded font-bold hover:bg-green-700">
                                        {editingId ? "Saqlash va Yangilash" : "Do'konga chiqarish"}
                                    </button>
                                </form>

                                <h3 className="text-lg font-bold mt-8 mb-4">Tovarlar Ro'yxati:</h3>
                                <div className="divide-y">
                                    {products.map(p => (
                                        <div key={p.id} className="py-2 flex justify-between items-center">
                                            <span>{p.title} - <strong>{formatPrice(p.price)}</strong></span>
                                            <button onClick={() => startEdit(p)} className="bg-blue-500 text-white px-3 py-1 rounded text-xs">O'zgartirish</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="relative min-h-[400px]">
                                {/* Watermark Background Logo */}
                                <div className="absolute inset-0 opacity-5 pointer-events-none flex items-center justify-center overflow-hidden">
                                    <img src="/logo.jpg" className="w-[500px] h-[500px] object-cover rounded-full select-none" alt="Watermark Background" />
                                </div>
                                <div className="relative z-10">
                                    <div className="text-center mb-8">
                                        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Yangi Mavsum Erkaklar Kiyimlari</h2>
                                        <p className="text-gray-500 mt-2">VIGOR — Eng sara va sifatli modellar</p>
                                    </div>

                                    {products.length === 0 ? (
                                        <p className="text-center text-gray-500 py-12">Hozircha do'konda tovar yo'q. Admin panelga o'tib kiyim qo'shing!</p>
                                    ) : (
                                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                                            {products.map(product => (
                                                <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden flex flex-col justify-between border hover:shadow-xl transition">
                                                    <img src={product.image} alt={product.title} className="w-full h-64 object-cover" onError={(e)=>{e.target.src='https://images.unsplash.com/photo-1516257984-b1b4d707412e?q=80&w=500'}} />
                                                    <div className="p-4 flex-grow flex flex-col justify-between">
                                                        <div>
                                                            <h3 className="font-bold text-lg text-gray-800 line-clamp-2">{product.title}</h3>
                                                            <p className="text-gray-500 text-xs mt-1">🧵 Mato: <span className="text-gray-700 font-medium">{product.fabric}</span></p>
                                                            <p className="text-gray-500 text-xs mt-0.5">📏 Razmerlar: <span className="text-gray-700 font-medium">{product.sizes}</span></p>
                                                        </div>
                                                        <div className="mt-4">
                                                            <div className="text-xl font-extrabold text-black mb-3">{formatPrice(product.price)}</div>
                                                            <button onClick={() => openTelegram(product)} className="w-full bg-black text-white py-2 rounded font-semibold hover:bg-yellow-600 hover:text-black transition">
                                                                Telegram orqali olish
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </main>
                    <footer className="bg-gray-900 text-gray-400 text-center py-6 text-sm border-t border-gray-800">
                        <p>&copy; 2026 VIGOR Brand. Barcha huquqlar himoyalangan.</p>
                    </footer>
                </div>
            );
        }
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>"""

class VigorRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, content, status=200, content_type='application/json'):
        content_bytes = content.encode('utf-8') if isinstance(content, str) else content
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content_bytes)

    def do_GET(self):
        if self.path == '/':
            self._send_response(HTML_CONTENT, status=200, content_type='text/html; charset=utf-8')
        elif self.path == '/api/products':
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    data = f.read()
                self._send_response(data)
            except Exception as e:
                self._send_response(json.dumps({"error": str(e)}), status=500)
        elif self.path == '/logo.jpg':
            try:
                logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.jpg')
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                self._send_response(logo_data, content_type='image/jpeg')
            except Exception as e:
                self._send_response(json.dumps({"error": str(e)}), status=500)
        else:
            self._send_response(json.dumps({"error": "Not Found"}), status=404)

    def do_POST(self):
        if self.path == '/api/products':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                new_product = json.loads(post_data.decode('utf-8'))
                new_product['id'] = int(time.time() * 1000)

                with open(DB_FILE, 'r+', encoding='utf-8') as f:
                    products = json.loads(f.read() or '[]')
                    products.append(new_product)
                    f.seek(0)
                    f.write(json.dumps(products, indent=2, ensure_ascii=False))
                    f.truncate()

                self._send_response(json.dumps(new_product), status=201)
            except Exception as e:
                self._send_response(json.dumps({"error": str(e)}), status=500)
        else:
            self._send_response(json.dumps({"error": "Not Found"}), status=404)

    def do_PUT(self):
        if self.path.startswith('/api/products/'):
            product_id_str = self.path.split('/')[-1]
            try:
                product_id = int(product_id_str)
                content_length = int(self.headers.get('Content-Length', 0))
                put_data = self.rfile.read(content_length)
                update_fields = json.loads(put_data.decode('utf-8'))

                with open(DB_FILE, 'r+', encoding='utf-8') as f:
                    products = json.loads(f.read() or '[]')
                    for p in products:
                        if p.get('id') == product_id:
                            p.update(update_fields)
                    f.seek(0)
                    f.write(json.dumps(products, indent=2, ensure_ascii=False))
                    f.truncate()

                self._send_response(json.dumps({"success": True}))
            except Exception as e:
                self._send_response(json.dumps({"error": str(e)}), status=500)
        else:
            self._send_response(json.dumps({"error": "Not Found"}), status=404)

def run():
    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, VigorRequestHandler)
    print(f"Server muvaffaqiyatli yoqildi: http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run()
