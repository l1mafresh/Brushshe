from customtkinter import *
from customtkinter import filedialog
from CTkMenuBar import *
from CTkColorPicker import *
from CTkMessagebox import *
from PIL import Image, ImageDraw, ImageTk, ImageGrab
from tkinter import EventType, PhotoImage, font
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
        dropdown1.add_option(option="Експортувати на ПК", command=self.export)

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
        self.stickers = [
            Image.open("stickers/smile.png"),
            Image.open("stickers/flower.png"),
            Image.open("stickers/heart.png"),
            Image.open("stickers/okay.png"),
            Image.open("stickers/cheese.png"),
            Image.open("stickers/grass.png"),
            Image.open("stickers/rain.png"),
            Image.open("stickers/brucklin.png"),
            Image.open("stickers/strawberry.png"),
            Image.open("stickers/butterfly.png"),
            Image.open("stickers/flower2.png")
        ]

        add_text_menu = menu.add_cascade("Текст")
        dropdown4 = CustomDropdownMenu(widget=add_text_menu)
        dropdown4.add_option(option="Додати текст на малюнок", command=self.add_text_window_show)
        dropdown4.add_option(option="Налаштувати текст для вставлення", command=self.text_settings)

        frames_menu = menu.add_cascade("Рамки", command=self.show_frames_window)

        my_gallery_menu = menu.add_cascade("Моя галерея", command=self.show_gallery_window)

        about_menu = menu.add_cascade("Про Brushshe", command=self.about_program)

# Панель інструментів
        tools_frame = CTkFrame(self)
        tools_frame.pack(side=TOP, fill=X)

        clean_btn = CTkButton(tools_frame, text="Очистити все", command=self.clean_all)
        clean_btn.pack(side=LEFT, padx=1)
        
        eraser_icon = CTkImage(light_image=Image.open("icons/eraser.png"), size=(20, 20))
        eraser = CTkButton(tools_frame, text=None, width=35, image=eraser_icon, command=self.eraser)
        eraser.pack(side=LEFT, padx=1)

        self.brush_size_label = CTkLabel(tools_frame, text="Пензль:")
        self.brush_size_label.pack(side=LEFT, padx=1)

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
        self.tk_font = CTkFont(size=self.font_size)
        self.size_a = 100

        gc.disable() # бо ввімкнений gc думає що додані наліпки і текст - це сміття

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop_paint)

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

    def open_img(self):
        file_path = filedialog.askopenfilename(filetypes=[("Зображення", "*.png;*.jpg;*.jpeg;*.gif"), ("Всі файли", "*.*")])
        if file_path:
            try:
                image = Image.open(file_path)
                self.image = image
                self.draw = ImageDraw.Draw(self.image)
                self.canvas.delete("all")
                self.canvas.configure(bg="white")
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
            except Exception as e:
                open_error_msg = CTkMessagebox(title = "Ех, на жаль, це сталося",
                                               message = f"Помилка - неможливо відкрити файл: {e}",
                                               icon="icons/cry.png", icon_size=(100,100), sound=True)

    def export(self):
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
        def update_btn():
            for widget in stickers_frame.winfo_children():
                widget.destroy()
            row = 0
            column = 0
            for image in self.stickers:
                resized_image = image.resize((self.size_a, self.size_a))
                image = ImageTk.PhotoImage(resized_image)
                sticker_btn = CTkButton(stickers_frame, text=None, image=image, command=lambda img=image: self.set_current_sticker(img))
                sticker_btn.grid(row=row, column=column, padx=10, pady=10)
                column += 1
                if column == 2:
                    column = 0
                    row +=1
                    
        sticker_choose = CTkToplevel(app)
        sticker_choose.geometry("320x420")
        sticker_choose.title("Оберіть наліпку")
                
        tabview = CTkTabview(sticker_choose, command=update_btn)
        tabview.add("Обрати наліпку")
        tabview.add("Розмір наліпок")
        tabview.set("Обрати наліпку")
        tabview.pack()

        stickers_frame = CTkScrollableFrame(tabview.tab("Обрати наліпку"), width=300, height=400)
        stickers_frame.pack()

        self.st_size_label = CTkLabel(tabview.tab("Розмір наліпок"), text=self.size_a)
        self.st_size_label.pack()
        self.st_slider = CTkSlider(tabview.tab("Розмір наліпок"), from_=10, to=175, command=self.change_sticker_size)
        self.st_slider.set(self.size_a)
        self.st_slider.pack()
        set_default = CTkButton(tabview.tab("Розмір наліпок"), text="Повернути як було", command=self.set_default_stickers_size)
        set_default.pack()

        update_btn()

    def set_current_sticker(self, image): # Обрати наліпку
        self.current_sticker = image
        if self.current_sticker:
            self.canvas.bind("<Button-1>", self.add_sticker)

    def add_sticker(self, event): # Додати наліпку
        self.canvas.create_image(event.x, event.y, anchor='center', image=self.current_sticker)
        self.canvas.unbind("<Button-1>")

    def change_sticker_size(self, value):
        self.size_a = int(self.st_slider.get())
        self.st_size_label.configure(text=self.size_a)

    def set_default_stickers_size(self):
        self.size_a = 100
        self.st_size_label.configure(text=self.size_a)
        self.st_slider.set(self.size_a)

    def add_text_window_show(self): # Обрати текст
        dialog = CTkInputDialog(title="Введіть текст,", text="а потім клацніть на потрібне місце на малюнку")
        text = dialog.get_input()
        if text:
            self.canvas.bind("<Button-1>", lambda event, t=text: self.add_text(event, text))

    def add_text(self, event, text): # Додати текст
        self.canvas.create_text(event.x, event.y, text=text, fill=self.color, font=self.tk_font)
        self.canvas.unbind("<Button-1>")

    def text_settings(self):
        def change_text_size(size):
            self.font_size = int(size)
            self.tk_font.configure(size=self.font_size) 
            self.tx_size_label.configure(text=self.font_size)
            
        def optionmenu_callback(value):
            self.tk_font = CTkFont(family=value, size=self.font_size)
            
        text_settings = CTkToplevel(app)
        text_settings.title("Налаштувати текст")
        self.tx_size_label = CTkLabel(text_settings, text=self.font_size)
        self.tx_size_label.pack()
        tx_size_slider = CTkSlider(text_settings, from_=11, to=96, command=change_text_size)
        tx_size_slider.set(self.font_size)
        tx_size_slider.pack()

        fonts_label = CTkLabel(text_settings, text="Шрифти з системи:")
        fonts_label.pack()
        fonts = list(font.families())
        fonts_optionmenu = CTkOptionMenu(text_settings, values=fonts, command=optionmenu_callback)
        fonts_optionmenu.set(self.tk_font['family'])
        fonts_optionmenu.pack()

    def show_frames_window(self):
        def on_frames_click(index):
            selected_frame = frames[index]
            resized_image = selected_frame.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
            self.frame_image = ImageTk.PhotoImage(resized_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.frame_image)
            
        frames_win = CTkToplevel(app)
        frames_win.title("Рамки")

        frames_thumbnails = [
            CTkImage(light_image=Image.open("frames_preview/frame1.png"), size=(100,100)),
            CTkImage(light_image=Image.open("frames_preview/frame2.png"), size=(100,100)),
            CTkImage(light_image=Image.open("frames_preview/frame3.png"), size=(100,100))
            ]
        frames = [
            Image.open("frames/frame1.png"),
            Image.open("frames/frame2.png"),
            Image.open("frames/frame3.png")
            ]
        for i, image in enumerate(frames_thumbnails):
            frames_btn = CTkButton(frames_win, text=None, image=image, command=lambda i=i: on_frames_click(i))
            frames_btn.pack()
        
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
            self.canvas.configure(bg="white")
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
                                  message="Brushshe (Брашше) - програма для малювання, в якій можна створювати те, що Вам подобається.\n\nОрел на ім'я Brucklin (Браклін) - її талісман.\n\nhttps://github.com/l1mafresh/Brushshe\n\nv0.5.1",
                                  icon="icons/brucklin.png", icon_size=(150,191), option_1="ОК", height=400)

    def clean_all(self):
        self.canvas.delete("all")

    def change_brush_size(self, size):
        self.brush_size = int(size)
        self.size_slider_label.configure(text=self.brush_size)

    def eraser(self):
        self.color = self.canvas.cget('bg')
        self.brush_size_label.configure(text="Ластик:")
        
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
        self.brush_size_label.configure(text="Пензль:")

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
        self.brush_size_label.configure(text="Пензль:")

    def changecolor2(self):
        self.color = self.getcolor
        self.brush_size_label.configure(text="Пензль:")
        
app = Brushshe()
app.mainloop()
