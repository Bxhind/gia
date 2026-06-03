INSERT INTO users (username, password_hash, full_name, role, is_active)
VALUES ('admin', '$2y$12$o.Bpvsopyd67.jqq38CgYO6rtCkwg/i7IW5BBUbl2dL87nL2vMxLu', 'Администратор', 'admin', TRUE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO partner_types (name) VALUES
('Розничный магазин'),
('Оптовый клиент'),
('Рекламное агентство')
ON CONFLICT (name) DO NOTHING;

INSERT INTO product_types (name, coefficient) VALUES
('Полиграфия', 1.1500),
('Упаковка', 1.3000)
ON CONFLICT (name) DO NOTHING;

INSERT INTO material_types (name, defect_percent) VALUES
('Бумага', 1.50),
('Картон', 2.00)
ON CONFLICT (name) DO NOTHING;

INSERT INTO partners (partner_type_id, name, legal_address, inn, director_full_name, phone, email, rating)
SELECT pt.id, 'ООО Альфа Принт', '620000, г. Екатеринбург, ул. Ленина, д. 1', '6671000001', 'Иванов Иван Иванович', '+7 (343) 111-11-11', 'alpha@example.com', 8
FROM partner_types pt WHERE pt.name = 'Оптовый клиент'
ON CONFLICT DO NOTHING;

INSERT INTO partners (partner_type_id, name, legal_address, inn, director_full_name, phone, email, rating)
SELECT pt.id, 'ИП Смирнова', '620014, г. Екатеринбург, ул. Малышева, д. 25', '6672000002', 'Смирнова Анна Петровна', '+7 (343) 222-22-22', 'smirnova@example.com', 5
FROM partner_types pt WHERE pt.name = 'Розничный магазин'
ON CONFLICT DO NOTHING;

INSERT INTO partners (partner_type_id, name, legal_address, inn, director_full_name, phone, email, rating)
SELECT pt.id, 'РА Вектор', '620075, г. Екатеринбург, пр. Мира, д. 10', '6673000003', 'Петров Петр Сергеевич', '+7 (343) 333-33-33', 'vector@example.com', 9
FROM partner_types pt WHERE pt.name = 'Рекламное агентство'
ON CONFLICT DO NOTHING;

INSERT INTO products (article, product_type_id, name, description, min_partner_price)
SELECT 'PP-001', pt.id, 'Буклет А4', 'Полноцветный буклет', 18.50
FROM product_types pt WHERE pt.name = 'Полиграфия'
ON CONFLICT (article) DO NOTHING;

INSERT INTO products (article, product_type_id, name, description, min_partner_price)
SELECT 'PP-002', pt.id, 'Коробка брендированная', 'Картонная упаковка с печатью', 42.00
FROM product_types pt WHERE pt.name = 'Упаковка'
ON CONFLICT (article) DO NOTHING;

INSERT INTO materials (material_type_id, name, unit, quantity_in_stock, min_quantity)
SELECT mt.id, 'Бумага мелованная 130 г/м2', 'лист', 5000.000, 1000.000
FROM material_types mt WHERE mt.name = 'Бумага';

INSERT INTO materials (material_type_id, name, unit, quantity_in_stock, min_quantity)
SELECT mt.id, 'Картон белый', 'лист', 2300.000, 500.000
FROM material_types mt WHERE mt.name = 'Картон';

INSERT INTO sales_history (partner_id, product_id, quantity, sale_date)
SELECT p.id, pr.id, 12000, DATE '2025-09-10'
FROM partners p, products pr
WHERE p.name = 'ООО Альфа Принт' AND pr.article = 'PP-001';

INSERT INTO sales_history (partner_id, product_id, quantity, sale_date)
SELECT p.id, pr.id, 41000, DATE '2025-12-03'
FROM partners p, products pr
WHERE p.name = 'ООО Альфа Принт' AND pr.article = 'PP-002';

INSERT INTO sales_history (partner_id, product_id, quantity, sale_date)
SELECT p.id, pr.id, 7500, DATE '2026-01-20'
FROM partners p, products pr
WHERE p.name = 'ИП Смирнова' AND pr.article = 'PP-001';

INSERT INTO sales_history (partner_id, product_id, quantity, sale_date)
SELECT p.id, pr.id, 220000, DATE '2026-02-15'
FROM partners p, products pr
WHERE p.name = 'РА Вектор' AND pr.article = 'PP-001';

INSERT INTO sales_history (partner_id, product_id, quantity, sale_date)
SELECT p.id, pr.id, 95000, DATE '2026-03-01'
FROM partners p, products pr
WHERE p.name = 'РА Вектор' AND pr.article = 'PP-002';
