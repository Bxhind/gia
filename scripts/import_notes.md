# Ручной импорт данных из Excel в PostgreSQL

## Порядок заполнения таблиц

Сначала заполняются справочники, затем таблицы, которые на них ссылаются.

1. `partner_types`
2. `product_types`
3. `material_types`
4. `partners`
5. `products`
6. `materials`
7. `sales_history`

## Обязательные поля

### partner_types
- `name`

### product_types
- `name`
- `coefficient`

### material_types
- `name`
- `defect_percent`

### partners
- `partner_type_id`
- `name`
- `legal_address`
- `inn`
- `director_full_name`
- `phone`
- `email`
- `rating`

### products
- `product_type_id`
- `name`

### materials
- `material_type_id`
- `name`
- `unit`

### sales_history
- `partner_id`
- `product_id`
- `quantity`
- `sale_date`

## Как сопоставлять названия типов из Excel с id

Если в Excel указано название типа партнера, сначала найдите его `id`:

```sql
SELECT id, name FROM partner_types ORDER BY name;
```

Для типа продукции:

```sql
SELECT id, name, coefficient FROM product_types ORDER BY name;
```

Для типа материала:

```sql
SELECT id, name, defect_percent FROM material_types ORDER BY name;
```

При импорте в `partners`, `products`, `materials` нужно вставлять именно числовой `id`, а не текстовое название.

## Проверка импорта

Проверить количество строк:

```sql
SELECT 'partner_types' AS table_name, COUNT(*) FROM partner_types
UNION ALL
SELECT 'product_types', COUNT(*) FROM product_types
UNION ALL
SELECT 'material_types', COUNT(*) FROM material_types
UNION ALL
SELECT 'partners', COUNT(*) FROM partners
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'materials', COUNT(*) FROM materials
UNION ALL
SELECT 'sales_history', COUNT(*) FROM sales_history;
```

Проверить партнеров с типами:

```sql
SELECT p.id, pt.name AS partner_type, p.name, p.inn, p.rating
FROM partners p
JOIN partner_types pt ON pt.id = p.partner_type_id
ORDER BY p.name;
```

Проверить продажи:

```sql
SELECT p.name AS partner, pr.name AS product, sh.quantity, sh.sale_date
FROM sales_history sh
JOIN partners p ON p.id = sh.partner_id
JOIN products pr ON pr.id = sh.product_id
ORDER BY sh.sale_date DESC;
```

Проверить общую сумму продаж и будущую скидку:

```sql
SELECT p.name, COALESCE(SUM(sh.quantity), 0) AS total_quantity
FROM partners p
LEFT JOIN sales_history sh ON sh.partner_id = p.id
GROUP BY p.id
ORDER BY p.name;
```
