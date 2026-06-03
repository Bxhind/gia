COMPANY_NAME = "ПринтПлюс"
FONT_FAMILY = "Segoe UI"

WINDOW_TITLES = {
    "login": "ПринтПлюс — вход",
    "partners": "ПринтПлюс — партнеры",
    "partner_form_add": "ПринтПлюс — добавление партнера",
    "partner_form_edit": "ПринтПлюс — редактирование партнера",
    "sales_history": "ПринтПлюс — история продаж",
}

COLORS = {
    "background": "#FFFFFF", "secondary_background": "#EAF2FF",
    "accent": "#2F80ED", "accent_dark": "#1C63C7",
    "text": "#1F2937", "muted_text": "#6B7280",
}

BUTTON_LABELS = {
    "login": "Войти", "add_partner": "Добавить партнера", "logout": "Выйти",
    "edit": "Редактировать", "sales_history": "История продаж",
    "save": "Сохранить", "back": "Назад", "apply": "Применить", "reset": "Сбросить",
}

FORM_FIELDS = [
    ("name", "Наименование"), ("partner_type_id", "Тип партнера"), ("rating", "Рейтинг"),
    ("legal_address", "Юридический адрес"), ("inn", "ИНН"),
    ("director_full_name", "ФИО руководителя"), ("phone", "Телефон"), ("email", "Email"),
]

SORT_MODES = {
    "name_asc": "По наименованию А-Я", "name_desc": "По наименованию Я-А",
    "rating_asc": "По рейтингу по возрастанию", "rating_desc": "По рейтингу по убыванию",
    "discount_asc": "По скидке по возрастанию", "discount_desc": "По скидке по убыванию",
}

DISCOUNT_THRESHOLDS = [(300000, 15), (50000, 10), (10000, 5), (0, 0)]
