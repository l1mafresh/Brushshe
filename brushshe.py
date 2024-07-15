from customtkinter import *
from customtkinter import filedialog
from CTkMenuBar import *
from CTkColorPicker import *
from CTkMessagebox import *
from PIL import Image, ImageDraw, ImageTk, ImageGrab, ImageFont
from tkinter import EventType, PhotoImage
import gc
import os
import uuid

class Brushshe(CTk):
    def __init__(self):
        super().__init__()
        self.title("Brushshe")
        self.geometry("650x580")
        self.iconphoto(True, PhotoImage(file="icon.png"))
        set_default_color_theme("brushshe_theme.json")
        set_appearance_mode("system")
        self.protocol("WM_DELETE_WINDOW", self.when_closing)

    # -------------------- Інтерфейс --------------------
# Меню
        menu = CTkMenuBar(self)
        
        file_menu = menu.add_cascade("Файл")
        dropdown1 = CustomDropdownMenu(widget=file_menu)
        dropdown1.add_option(option="Відкрити з файлу", command=self.open_img)
        dropdown1.add_option(option="Зберегти малюнок на комп'ютер", command=self.save_img)

        mode_menu = menu.add_cascade("Режим")
        dropdown2 = CustomDropdownMenu(widget=mode_menu)
        dropdown2.add_option(option="Світлий", command=self.light_mode)
        dropdown2.add_option(option="Темний", command=self.dark_mode)

        bg_menu = menu.add_cascade("Колір тла")
        dropdown3 = CustomDropdownMenu(widget=bg_menu)
        ukr_colors = {
            "Білий": "white",
            "Червоний": "red",
            "Яскраво-зелений": "#2eff00",
            "Синій": "blue",
            "Жовтий": "yellow",
            "Фіолетовий": "purple",
            "Блакитний": "cyan",
            "Рожевий": "pink",
            "Помаранчевий": "orange",
            "Коричневий": "brown",
            "Сірий": "gray",
            "Чорний": "black"
        }
        for ukr_name, color in ukr_colors.items():
            dropdown3.add_option(option=ukr_name, command=lambda c=color: self.change_bg(c))
        dropdown3.add_separator()
        dropdown3.add_option(option="Інший колір", command=self.other_bg_color)

        stickers_menu = menu.add_cascade("Наліпки", command=self.show_sticker_choose)
        # ширина і висота всіх зображень стікерів - 88 px
        self.stickers = {
            "Смайл": Image.open("stickers/smile.png"),
            "Квітка": Image.open("stickers/flower.png"),
            "Серце": Image.open("stickers/heart.png"),
            "ОКей": Image.open("stickers/okay.png"),
            "Сир": Image.open("stickers/cheese.png"),
            "Трава": Image.open("stickers/grass.png"),
            "Дощ": Image.open("stickers/rain.png"),
            "Полуниця": Image.open("stickers/strawberry.png"),
            "Метелик": Image.open("stickers/butterfly.png"),
            "Квітка2": Image.open("stickers/flower2.png")
        }

        add_text_menu = menu.add_cascade("Текст")
        dropdown4 = CustomDropdownMenu(widget=add_text_menu)
        dropdown4.add_option(option="Додати текст на малюнок", command=self.add_text_window_show)
        dropdown4.add_option(option="Змінити розмір", command=self.change_text_size_show)

        my_gallery_menu = menu.add_cascade("Моя галерея", command=self.show_gallery_window)

        about_menu = menu.add_cascade("Про Brushshe", command=self.about_program)

# Панель інструментів
        tools_frame = CTkFrame(self)
        tools_frame.pack(side=TOP, fill=X)

        clean_btn = CTkButton(tools_frame, text="Очистити все", command=self.clean_all)
        clean_btn.pack(side=LEFT, padx=1)

        brush_size_label = CTkLabel(tools_frame, text="Пензль:")
        brush_size_label.pack(side=LEFT, padx=1)

        size_slider = CTkSlider(tools_frame, from_=1, to=50, command=self.change_brush_size)
        self.brush_size = 2
        size_slider.set(self.brush_size)
        size_slider.pack(side=LEFT, padx=5)

        self.size_slider_label = CTkLabel(tools_frame, text="2")
        self.size_slider_label.pack(side=LEFT, padx=1)

        save_in_gallery_button = CTkButton(tools_frame, text="Зберегти в галерею", command=self.save_in_gallery)
        save_in_gallery_button.pack(side=RIGHT, padx=5)

# Канва
        self.canvas = CTkCanvas(self, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)

# Панель кольорів
        self.color_frame = CTkFrame(self)
        self.color_frame.pack(side=BOTTOM, fill=X)

        self.colors = [
            "black", "red", "#2eff00", "blue", "yellow", "purple",
            "cyan", "pink", "orange", "brown", "gray", "white"
            ]
        for color in self.colors:
            color_btn = CTkButton(self.color_frame, fg_color=color, text=None, width=35,
                                  border_width=2, command=lambda c=color: self.change_color(c))
            color_btn.pack(side=LEFT, padx=1)

        other_color = CTkButton(self.color_frame, text="Інший", width=70, command=self.other_color_choise)
        other_color.pack(side=RIGHT, padx=1)

        self.other_color_btn = CTkButton(self.color_frame, text=None, width=35, border_width=2, command=self.changecolor2)

    # -------------------- Ініціалізація --------------------
        self.color = "black"

        self.image = Image.new("RGB", (800, 600), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.photo = None

        self.prev_x = None
        self.prev_y = None

        self.font_size = 24
        self.size_a = 100

        gc.disable() # бо ввімкнений gc думає що додані наліпки і текст - це сміття

        self.setup_initialize()

    def setup_initialize(self):
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop_paint)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # -------------------- Функціонал --------------------
    def when_closing(self):
        closing_msg = CTkMessagebox(title = "Ви покидаєте Brushshe", message = "Зберегти малюнок?",
                                    option_1="Ні", option_2="Зберегти", option_3="Назад в Brushshe",
                                    icon="icons/question.png", icon_size=(100,100), sound=True)
        response = closing_msg.get()
        if response == "Ні":
            app.destroy()
        elif response == "Зберегти":
            self.save_in_gallery()
        else:
            pass

    def paint(self, cur):
        if self.prev_x and self.prev_y:
            self.canvas.create_line(self.prev_x, self.prev_y, cur.x, cur.y, width=self.brush_size, fill=self.color,
                               smooth=True, capstyle=ROUND)
        self.prev_x, self.prev_y = cur.x, cur.y

    def stop_paint(self, cur):
        self.prev_x, self.prev_y = (None, None)

    def on_canvas_click(self, event):
        if hasattr (self, "current_sticker") and self.current_sticker:
            self.add_sticker(self.current_sticker, event.x, event.y)
            self.current_sticker = None

    def open_img(self):
        file_path = filedialog.askopenfilename(filetypes=[("Зображення", "*.png;*.jpg;*.jpeg;*.gif"), ("Всі файли", "*.*")])
        if file_path:
            try:
                image = Image.open(file_path)
                self.image = image
                self.draw = ImageDraw.Draw(self.image)
                self.canvas.delete("all")
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
            except Exception as e:
                open_error_msg = CTkMessagebox(title = "Ех, на жаль, це сталося",
                                               message = f"Помилка - неможливо відкрити файл: {e}",
                                               icon="icons/cry.png", icon_size=(100,100), sound=True)

    def save_img(self):
        # позиції канви
        x0 = self.canvas.winfo_rootx()
        y0 = self.canvas.winfo_rooty()
        x1 = x0 + self.canvas.winfo_width()
        y1 = y0 + self.canvas.winfo_height()

        # вміст канви
        canvas_img = ImageGrab.grab(bbox=(x0, y0, x1, y1))

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG файли", "*.png"), ("Всі файли", "*.*")])
        if file_path:
            canvas_img.save(file_path)

    def light_mode(self):
        set_appearance_mode("light")

    def dark_mode(self):
        set_appearance_mode("dark")

    def change_bg(self, new_color):
        self.canvas.configure(bg=new_color)

    def other_bg_color(self):
        pick_color = AskColor(title="Оберіть інший колір тла")
        bg_getcolor = pick_color.get()
        if bg_getcolor:
            self.canvas.configure(bg=bg_getcolor)
        
    def show_sticker_choose(self):
        sticker_choose = CTkToplevel(app)
        sticker_choose.geometry("300x420")
        sticker_choose.title("Оберіть наліпку")

        # Segmented Button
        def segmented_button_callback(value):
            for widget in stickers_frame.winfo_children():
                widget.destroy()
                
            if value == "Обрати наліпку":
                row = 0
                column = 0
                for name, image in self.stickers.items():
                    resized_image = image.resize((self.size_a, self.size_a))
                    image = ImageTk.PhotoImage(resized_image)
                    sticker_btn = CTkButton(stickers_frame, text=None, image=image,
                                            command=lambda img=image: self.set_current_sticker(img))
                    sticker_btn.grid(row=row, column=column, padx=10, pady=10)
                    column += 1
                    if column == 2:
                        column = 0
                        row +=1
            elif value == "Розмір наліпок":
                self.st_size_label = CTkLabel(stickers_frame, text=self.size_a)
                self.st_size_label.pack()
                self.st_slider = CTkSlider(stickers_frame, from_=10, to=175, command=self.change_sticker_size)
                self.st_slider.set(self.size_a)
                self.st_slider.pack()
                set_default = CTkButton(stickers_frame, text="Повернути як було", command=self.set_default_stickers_size)
                set_default.pack()
                
        segemented_button = CTkSegmentedButton(sticker_choose, values=["Обрати наліпку", "Розмір наліпок"],
                                                     command=segmented_button_callback)
        segemented_button.set("Обрати наліпку")
        segemented_button.pack()
        
        # Фрейм
        stickers_frame = CTkScrollableFrame(sticker_choose, width=300, height=400)
        stickers_frame.pack()

        segmented_button_callback("Обрати наліпку")

    def add_sticker(self, image, x, y):
        self.canvas.create_image(x, y, anchor=CENTER, image=image)

    def set_current_sticker(self, image):
        self.current_sticker = image

    def change_sticker_size(self, value):
        self.size_a = int(self.st_slider.get())
        self.st_size_label.configure(text=self.size_a)

    def set_default_stickers_size(self):
        self.size_a = 100
        self.st_size_label.configure(text=self.size_a)
        self.st_slider.set(self.size_a)

    def add_text_window_show(self):
        dialog = CTkInputDialog(title="Введіть текст,", text="а потім клацніть на потрібне місце на малюнку")
        text = dialog.get_input()
        if text:
            self.canvas.bind("<Button-1>", lambda event, t=text: self.add_text(event, text))

    def add_text(self, event, text):
        tk_font = CTkFont(size=self.font_size)
        self.canvas.create_text(event.x, event.y, text=text, fill=self.color, font=tk_font)
        self.canvas.unbind("<Button-1>")
        self.setup_initialize()

    def change_text_size_show(self):
        change_tx_size = CTkToplevel(app)
        change_tx_size.title("Змінити розмір тексту")
        self.tx_size_label = CTkLabel(change_tx_size, text=self.font_size)
        self.tx_size_label.pack()
        tx_size_slider = CTkSlider(change_tx_size, from_=11, to=96, command=self.change_text_size)
        tx_size_slider.set(self.font_size)
        tx_size_slider.pack()

    def change_text_size(self, size):
        self.font_size = int(size)
        self.tx_size_label.configure(text=self.font_size)

    def show_gallery_window(self):
        my_gallery = CTkToplevel(app)
        my_gallery.title("Галерея Brushshe")
        my_gallery.geometry("650x580")

        title_label = CTkLabel(my_gallery, text="Моя галерея")
        title_label.pack()

        gallery_frame = CTkScrollableFrame(my_gallery, width=650, height=560)
        gallery_frame.pack()

        row = 0
        column = 0

        def open_from_gallery(img_path):
            image = Image.open(img_path)
            self.image = image
            self.draw = ImageDraw.Draw(self.image)
            self.canvas.delete("all")
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
                
        for filename in os.listdir("gallery"):
            if filename.endswith(".png"):
                img_path = os.path.join("gallery", filename)
                img = Image.open(img_path)

                button_image = CTkImage(img, size=(250, 250))
                image_button = CTkButton(gallery_frame, image=button_image, text=None, command=lambda img_path=img_path: open_from_gallery(img_path))
                image_button.grid(row=row, column=column, padx=10, pady=10)
                
                column += 1
                if column == 2:
                    column = 0
                    row +=1
        
    def about_program(self):
        about_msg = CTkMessagebox(title="Про програму",
                                  message="Brushshe (Брашше) - програма для малювання, в якій можна створювати те, що Вам подобається.\n\nОрел на ім'я Brucklin (Браклін) - її талісман.\n\nhttps://github.com/l1mafresh/Brushshe\n\nv0.4.1",
                                  icon="icons/brucklin.png", icon_size=(150,191), option_1="Зрозуміло", height=400)

    def clean_all(self):
        self.canvas.delete("all")

    def change_brush_size(self, size):
        self.brush_size = int(size)
        self.size_slider_label.configure(text=self.brush_size)

    def save_in_gallery(self):
        # позиції канви
        x0 = self.canvas.winfo_rootx()
        y0 = self.canvas.winfo_rooty()
        x1 = x0 + self.canvas.winfo_width()
        y1 = y0 + self.canvas.winfo_height()

        # вміст канви
        canvas_img = ImageGrab.grab(bbox=(x0, y0, x1, y1))

        unique_filename = f"gallery/{uuid.uuid4()}.png"

        saved = CTkMessagebox(title="Збережено",
                              message='Малюнок успішно збережено в галерею ("Моя галерея" в меню вгорі)!',
                              icon="icons/saved.png", icon_size=(100,100))

        canvas_img.save(unique_filename)

    def change_color(self, new_color):
        self.color = new_color
        pass

    def other_color_choise(self):
        try:
            pick_color = AskColor(title = "Оберіть інший колір пензля")
            self.getcolor = pick_color.get()
            if self.getcolor:
                self.color = self.getcolor
                self.show_other_color_btn()
        except:
            pass
        
    def show_other_color_btn(self):
        self.other_color_btn.pack(side=RIGHT, padx=1)
        self.other_color_btn.configure(fg_color=self.getcolor)

    def changecolor2(self):
        self.color = self.getcolor
        
app = Brushshe()
app.mainloop()
