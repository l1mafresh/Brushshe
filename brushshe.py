from customtkinter import *
from customtkinter import filedialog
from CTkMenuBar import *
from CTkColorPicker import *
from CTkMessagebox import *
from PIL import Image, ImageDraw, ImageTk, ImageGrab
from tkinter import EventType, PhotoImage

class Brushshe(CTk):
    def __init__(self):
        super().__init__()
        self.title("Brushshe")
        self.geometry("650x580+100+70")
        self.iconphoto(True, PhotoImage(file="icon.png"))
        set_default_color_theme("brushshe_theme.json")

        self.protocol("WM_DELETE_WINDOW", self.when_closing)

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

        bg_menu = menu.add_cascade("Тло")
        dropdown3 = CustomDropdownMenu(widget=bg_menu)
        ukr_colors = {
            "Білий": "white",
            "Червоний": "red",
            "Зелений": "#2eff00",
            "Синій": "blue",
            "Жовтий": "yellow",
            "Фіолетовий": "purple",
            "Блакитний": "cyan",
            "Пурпурний": "magenta",
            "Помаранчевий": "orange",
            "Коричневий": "brown",
            "Сірий": "gray",
            "Чорний": "black"
        }
        for ukr_name, color in ukr_colors.items():
            dropdown3.add_option(option=ukr_name, command=lambda c=color: self.change_bg(c))

        self.stickers = {
            "Смайл": Image.open("stickers/smile.png"),
            "Квітка": Image.open("stickers/flower.png"),
            "Серце": Image.open("stickers/heart.png"),
            "ОКей": Image.open("stickers/okay.png"),
            "Сир": Image.open("stickers/cheese.png")
        }

        stickers_menu = menu.add_cascade("Наліпки")
        dropdown4 = CustomDropdownMenu(widget=stickers_menu)
        for name, image in self.stickers.items():
            image = ImageTk.PhotoImage(image)
            dropdown4.add_option(option=name, image=image, compound="left", command=lambda img=image: self.set_current_sticker(img))

        about_menu = menu.add_cascade("Про Brushshe", command=self.about_program)

        # Панель інструментів
        tools_frame = CTkFrame(self)
        tools_frame.pack(side=TOP, fill=X)

        clean_btn = CTkButton(tools_frame, text="Очистити все", command=self.clean_all)
        clean_btn.pack(side=LEFT, padx=1)

        brush_size_label = CTkLabel(tools_frame, text="Пензль:")
        brush_size_label.pack(side=LEFT, padx=1)

        size_scale = CTkSlider(tools_frame, from_=1, to=50, command=self.change_brush_size)
        self.brush_size = 2
        size_scale.set(self.brush_size)
        size_scale.pack(side=LEFT, padx=5)

        # Канва
        self.canvas = CTkCanvas(self, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)

        # Панель кольорів
        self.color_frame = CTkFrame(self)
        self.color_frame.pack(side=BOTTOM, fill=X)

        self.colors = ["black", "red", "#2eff00", "blue", "yellow", "purple", "cyan", "magenta", "orange", "brown", "gray", "white"]
        for color in self.colors:
            color_btn = CTkButton(self.color_frame, fg_color=color, text=None, width=35, command=lambda c=color: self.change_color(c))
            color_btn.pack(side=LEFT, padx=1)

        other_color = CTkButton(self.color_frame, text="Інший", width=70, command=self.other_color_choise)
        other_color.pack(side=RIGHT, padx=1)

        self.other_color_btn = CTkButton(self.color_frame, text=None, width=35, command=self.changecolor2)

        # Інше
        self.color = "black"

        self.image = Image.new("RGB", (800, 600), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.photo = None

        self.prev_x = None
        self.prev_y = None
        
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.stoppaint)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def when_closing(self):
        closing_msg = CTkMessagebox(title = "Ви покидаєте Brushshe", message = "Зберегти малюнок?",
                                    option_1="Ні", option_2="Зберегти", option_3="Назад в Brushshe",
                                    icon="icons/question.png", icon_size=(100,100))
        response = closing_msg.get()
        if response=="Ні":
            app.destroy()
        elif response== "Зберегти":
            self.save_img()
        else:
            pass

    def paint(self, cur):
        if self.prev_x is not None and self.prev_y is not None:
            self.canvas.create_line(self.prev_x, self.prev_y, cur.x, cur.y, width=self.brush_size, fill=self.color,
                               smooth=True, capstyle=ROUND)
        self.prev_x, self.prev_y = cur.x, cur.y

    def stoppaint(self, cur):
        self.prev_x, self.prev_y = (None, None)

    def on_canvas_click(self, event):
        if hasattr (self, "current_sticker") and self.current_sticker:
            self.add_sticker(self.current_sticker, event.x, event.y)
            self.current_sticker = None

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
                open_error_msg = CTkMessagebox(title = "Ех, на жаль, це сталося", message = f"Помилка - неможливо відкрити файл: {e}",
                                               icon="icons/cry.png", icon_size=(100,100))

    def light_mode(self):
        set_appearance_mode("light")

    def dark_mode(self):
        set_appearance_mode("dark")

    def change_bg(self, new_color):
        self.canvas.configure(bg=new_color)

    def add_sticker(self, image, x, y):
        self.canvas.create_image(x, y, anchor=CENTER, image=image)

    def set_current_sticker(self, image):
        self.current_sticker = image

    def about_program(self):
        about_msg = CTkMessagebox(title="Про програму",
                                  message="Brushshe (Брашше) - програма для малювання, в якій можна створювати те, що Вам подобається.\nОрел на ім'я Brucklin (Браклін) - її талісман.\nhttps://github.com/l1mafresh/Brushshe\nv0.1",
                                  icon="icons/brucklin.png", icon_size=(150,191), option_1="Зрозуміло", width=400, height=400)

    def clean_all(self):
        self.canvas.delete("all")

    def change_brush_size(self, size):
        self.brush_size = int(size)

    def change_color(self, new_color):
        self.color = new_color

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
