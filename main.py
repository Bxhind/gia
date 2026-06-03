from tkinter import messagebox

from database.connection import check_database_connection, get_database_error_text
from ui.app import PrintPlusApp


def main() -> None:
    if not check_database_connection():
        messagebox.showerror(
            "Ошибка подключения к базе данных",
            get_database_error_text(),
        )
        return

    app = PrintPlusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
