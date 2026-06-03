import tkinter as tk
from tkinter import messagebox, ttk

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from config.app_config import ICON_PATH, LOGO_PATH
from config.domain_config import BUTTON_LABELS, COLORS, FONT_FAMILY, FORM_FIELDS, SORT_MODES, WINDOW_TITLES
from database.connection import SessionLocal
from models import Partner, PartnerType, Sale
from services import authenticate, calculate_partner_discount, validate_partner


class PrintPlusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.session = SessionLocal()
        self.logo_image = None
        self.vars = {}
        self.partner_types = []
        self.title(WINDOW_TITLES["login"])
        self.geometry("980x700")
        self.minsize(840, 560)
        if ICON_PATH.exists():
            try:
                self.iconbitmap(ICON_PATH)
            except tk.TclError:
                pass
        self.configure(bg=COLORS["background"])
        self._style()
        self.body = ttk.Frame(self, padding=18)
        self.body.pack(fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.show_login()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=(FONT_FAMILY, 10), background=COLORS["background"], foreground=COLORS["text"])
        style.configure("TFrame", background=COLORS["background"])
        style.configure("Box.TFrame", background=COLORS["secondary_background"], relief="solid", borderwidth=1)
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
        style.configure("Box.TLabel", background=COLORS["secondary_background"])
        style.configure("Title.TLabel", font=(FONT_FAMILY, 20, "bold"))
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="#FFFFFF", padding=(12, 6))
        style.map("Accent.TButton", background=[("active", COLORS["accent_dark"])])
        style.configure("Treeview", rowheight=28)

    def clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def close(self):
        self.session.close()
        self.destroy()

    def show_login(self):
        self.clear()
        self.title(WINDOW_TITLES["login"])
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)
        box = ttk.Frame(self.body, padding=32, style="Box.TFrame")
        box.grid(row=0, column=0)
        ttk.Label(box, text="ПринтПлюс\nВход в систему", font=(FONT_FAMILY, 20, "bold"), style="Box.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 24))
        username, password = tk.StringVar(), tk.StringVar()
        for row, (text, var, show) in enumerate([("Логин", username, ""), ("Пароль", password, "*")], start=1):
            ttk.Label(box, text=text, style="Box.TLabel").grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(box, textvariable=var, show=show, width=32)
            entry.grid(row=row, column=1, pady=6)
            entry.bind("<Return>", lambda _e: self.login(username.get(), password.get()))
            if row == 1:
                entry.focus_set()
        ttk.Button(box, text=BUTTON_LABELS["login"], style="Accent.TButton", command=lambda: self.login(username.get(), password.get())).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(18, 0))

    def login(self, username, password):
        try:
            user, error = authenticate(self.session, username, password)
        except Exception as exc:
            messagebox.showerror("Ошибка авторизации", f"Не удалось проверить пользователя: {exc}")
            return
        if error:
            messagebox.showerror("Ошибка входа", error)
            return
        self.current_user = user
        self.show_partners()

    def show_partners(self):
        self.clear()
        self.title(WINDOW_TITLES["partners"])
        self.search = tk.StringVar()
        self.type_filter = tk.StringVar(value="Все типы")
        self.sort_mode = tk.StringVar(value=SORT_MODES["name_asc"])
        self.partner_types = list(self.session.scalars(select(PartnerType).order_by(PartnerType.name)))

        header = ttk.Frame(self.body)
        header.pack(fill="x", pady=(0, 14))
        self._logo(header).pack(side="left", padx=(0, 14))
        ttk.Label(header, text="Партнеры", style="Title.TLabel").pack(side="left", expand=True, anchor="w")
        ttk.Button(header, text=BUTTON_LABELS["add_partner"], style="Accent.TButton", command=lambda: self.show_form()).pack(side="left", padx=6)
        ttk.Button(header, text=BUTTON_LABELS["logout"], command=self.show_login).pack(side="left")

        filters = ttk.Frame(self.body, padding=12, style="Box.TFrame")
        filters.pack(fill="x", pady=(0, 12))
        for i in (1,):
            filters.columnconfigure(i, weight=1)
        ttk.Label(filters, text="Поиск", style="Box.TLabel").grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(filters, textvariable=self.search).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Label(filters, text="Тип", style="Box.TLabel").grid(row=0, column=2, padx=(0, 8))
        ttk.Combobox(filters, textvariable=self.type_filter, state="readonly", width=22, values=["Все типы"] + [t.name for t in self.partner_types]).grid(row=0, column=3, padx=(0, 10))
        ttk.Label(filters, text="Сортировка", style="Box.TLabel").grid(row=0, column=4, padx=(0, 8))
        ttk.Combobox(filters, textvariable=self.sort_mode, state="readonly", width=28, values=list(SORT_MODES.values())).grid(row=0, column=5, padx=(0, 10))
        ttk.Button(filters, text=BUTTON_LABELS["apply"], command=self.load_partners).grid(row=0, column=6, padx=(0, 6))
        ttk.Button(filters, text=BUTTON_LABELS["reset"], command=self.reset_filters).grid(row=0, column=7)

        self.canvas = tk.Canvas(self.body, bg=COLORS["background"], highlightthickness=0)
        scroll = ttk.Scrollbar(self.body, orient="vertical", command=self.canvas.yview)
        self.cards = ttk.Frame(self.canvas)
        self.cards.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        window = self.canvas.create_window((0, 0), window=self.cards, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(window, width=e.width))
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.load_partners()

    def _logo(self, parent):
        if LOGO_PATH.exists():
            try:
                self.logo_image = tk.PhotoImage(file=LOGO_PATH)
                return tk.Label(parent, image=self.logo_image, bg=COLORS["background"])
            except tk.TclError:
                pass
        return tk.Label(parent, text="Лого", width=12, height=3, bg=COLORS["secondary_background"], fg=COLORS["muted_text"], relief="ridge")

    def selected_type_id(self):
        return next((t.id for t in self.partner_types if t.name == self.type_filter.get()), None)

    def sort_key(self):
        return next((k for k, v in SORT_MODES.items() if v == self.sort_mode.get()), "name_asc")

    def load_partners(self):
        for widget in self.cards.winfo_children():
            widget.destroy()
        try:
            items = self.query_partners()
        except Exception as exc:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить партнеров: {exc}")
            return
        if not items:
            ttk.Label(self.cards, text="Партнеры не найдены").pack(pady=24)
        for partner, total, discount in items:
            self.partner_card(partner, discount)

    def query_partners(self):
        total = func.coalesce(func.sum(Sale.quantity), 0)
        query = select(Partner, total).outerjoin(Sale).options(selectinload(Partner.partner_type)).group_by(Partner.id)
        if self.search.get().strip():
            s = f"%{self.search.get().strip()}%"
            query = query.where(or_(Partner.name.ilike(s), Partner.director_full_name.ilike(s), Partner.phone.ilike(s), Partner.email.ilike(s), Partner.inn.ilike(s)))
        if self.selected_type_id():
            query = query.where(Partner.partner_type_id == self.selected_type_id())
        key = self.sort_key()
        orders = {"name_asc": Partner.name.asc(), "name_desc": Partner.name.desc(), "rating_asc": Partner.rating.asc(), "rating_desc": Partner.rating.desc()}
        query = query.order_by(orders.get(key, Partner.name.asc()))
        rows = [(p, int(q or 0), calculate_partner_discount(int(q or 0))) for p, q in self.session.execute(query)]
        if key == "discount_asc":
            rows.sort(key=lambda x: (x[2], x[0].name.lower()))
        if key == "discount_desc":
            rows.sort(key=lambda x: (-x[2], x[0].name.lower()))
        return rows

    def partner_card(self, partner, discount):
        card = ttk.Frame(self.cards, padding=14, style="Box.TFrame")
        card.pack(fill="x", pady=6)
        card.columnconfigure(0, weight=1)
        lines = [f"{partner.partner_type.name} | {partner.name}", partner.director_full_name, partner.phone, f"Рейтинг: {partner.rating}", f"Скидка: {discount}%"]
        for row, text in enumerate(lines):
            ttk.Label(card, text=text, style="Box.TLabel", font=(FONT_FAMILY, 11, "bold") if row == 0 else None).grid(row=row, column=0, sticky="w", pady=2)
        buttons = ttk.Frame(card, style="Box.TFrame")
        buttons.grid(row=0, column=1, rowspan=5, sticky="e")
        ttk.Button(buttons, text=BUTTON_LABELS["edit"], command=lambda: self.show_form(partner.id)).pack(fill="x", pady=(0, 6))
        ttk.Button(buttons, text=BUTTON_LABELS["sales_history"], command=lambda: self.show_history(partner.id)).pack(fill="x")

    def reset_filters(self):
        self.search.set("")
        self.type_filter.set("Все типы")
        self.sort_mode.set(SORT_MODES["name_asc"])
        self.load_partners()

    def show_form(self, partner_id=None):
        self.clear()
        partner = self.session.get(Partner, partner_id) if partner_id else None
        self.title(WINDOW_TITLES["partner_form_edit"] if partner else WINDOW_TITLES["partner_form_add"])
        ttk.Label(self.body, text="Редактирование партнера" if partner else "Добавление партнера", style="Title.TLabel").pack(anchor="w", pady=(0, 18))
        form = ttk.Frame(self.body, padding=16, style="Box.TFrame")
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        self.partner_types = list(self.session.scalars(select(PartnerType).order_by(PartnerType.name)))
        self.vars = {name: tk.StringVar() for name, _ in FORM_FIELDS}
        if partner:
            values = {k: getattr(partner, k) for k, _ in FORM_FIELDS if k != "partner_type_id"}
            values["partner_type_id"] = partner.partner_type.name
            for key, value in values.items():
                self.vars[key].set(str(value))
        for row, (name, label) in enumerate(FORM_FIELDS):
            ttk.Label(form, text=label, style="Box.TLabel").grid(row=row, column=0, sticky="w", pady=6, padx=(0, 12))
            if name == "partner_type_id":
                ttk.Combobox(form, textvariable=self.vars[name], state="readonly", values=[t.name for t in self.partner_types]).grid(row=row, column=1, sticky="ew", pady=6)
            else:
                ttk.Entry(form, textvariable=self.vars[name]).grid(row=row, column=1, sticky="ew", pady=6)
        buttons = ttk.Frame(self.body)
        buttons.pack(anchor="e", pady=18)
        ttk.Button(buttons, text=BUTTON_LABELS["back"], command=self.show_partners).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=BUTTON_LABELS["save"], style="Accent.TButton", command=lambda: self.save_partner(partner)).pack(side="left")

    def form_data(self):
        type_id = next((t.id for t in self.partner_types if t.name == self.vars["partner_type_id"].get()), None)
        return {**{k: v.get().strip() for k, v in self.vars.items() if k != "partner_type_id"}, "partner_type_id": type_id}

    def save_partner(self, partner):
        data = self.form_data()
        errors = validate_partner(data)
        if errors:
            messagebox.showerror("Ошибка валидации", "\n".join(errors))
            return
        data["rating"] = int(data["rating"])
        try:
            if partner is None:
                self.session.add(Partner(**data))
            else:
                for key, value in data.items():
                    setattr(partner, key, value)
            self.session.commit()
            messagebox.showinfo("Сохранение", "Данные партнера сохранены.")
            self.show_partners()
        except Exception as exc:
            self.session.rollback()
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить партнера: {exc}")

    def show_history(self, partner_id):
        self.clear()
        self.title(WINDOW_TITLES["sales_history"])
        partner = self.session.get(Partner, partner_id)
        ttk.Label(self.body, text=f"История продаж: {partner.name}", style="Title.TLabel").pack(anchor="w", pady=(0, 16))
        tree = ttk.Treeview(self.body, columns=("product", "quantity", "date"), show="headings")
        for key, text, width in [("product", "Продукция", 420), ("quantity", "Количество", 120), ("date", "Дата продажи", 140)]:
            tree.heading(key, text=text)
            tree.column(key, width=width, anchor="center" if key != "product" else "w")
        tree.pack(fill="both", expand=True)
        sales = self.session.scalars(select(Sale).where(Sale.partner_id == partner_id).options(selectinload(Sale.product)).order_by(Sale.sale_date.desc()))
        for sale in sales:
            tree.insert("", "end", values=(sale.product.name, sale.quantity, sale.sale_date.strftime("%d.%m.%Y")))
        ttk.Button(self.body, text=BUTTON_LABELS["back"], command=self.show_partners).pack(anchor="e", pady=16)
