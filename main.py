import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


# ==========================================
# EXERCISE CLASS
# ==========================================
class Exercise:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.completed = False

    def markAsCompleted(self):
        self.completed = True

    def isCompleted(self):
        return self.completed


# ==========================================
# PROGRESS TRACKER CLASS
# ==========================================
class ProgressTracker:
    def __init__(self, totalExercises):
        self.completed = 0
        self.totalExercises = totalExercises
        self.progressRate = 0.0

    def markCompleted(self, ex: Exercise):
        if not ex.isCompleted():
            ex.markAsCompleted()
            self.completed += 1
            self.calculateProgress()

    def calculateProgress(self):
        if self.totalExercises == 0:
            self.progressRate = 0
        else:
            self.progressRate = self.completed / self.totalExercises
        return self.progressRate

    def displayProgress(self):
        return f"{self.completed} / {self.totalExercises}"


# ==========================================
# MAIN APPLICATION
# ==========================================
class FITasticFlexieTimer:

    DATA_FILE = "fitness_data.json"

    def __init__(self, root):

        self.root = root
        self.root.title("FITastic Flexie Timer")
        self.root.state("zoomed")
        self.root.configure(bg="#EAF4FF")

        # COLORS
        self.primary = "#4A90E2"
        self.secondary = "#50E3C2"
        self.dark = "#1E293B"
        self.light = "#FFFFFF"
        self.bg = "#EAF4FF"
        self.accent = "#FF6B6B"

        # USER DATA
        self.user_name = tk.StringVar()
        self.user_weight = tk.StringVar()

        # TIMER
        self.current_exercise = None
        self.time_left = 0
        self.after_id = None

        # AVAILABILITY
        self.availability = {}

        # WEEKLY PLAN
        self.weekly_plan = {
            "Monday": [Exercise("Push Ups", 30), Exercise("Jumping Jacks", 45), Exercise("Plank", 60)],
            "Tuesday": [Exercise("Squats", 45), Exercise("Lunges", 40), Exercise("Mountain Climbers", 50)],
            "Wednesday": [Exercise("Sit Ups", 40), Exercise("Burpees", 50), Exercise("Jogging", 120)],
            "Thursday": [Exercise("High Knees", 45), Exercise("Push Ups", 30), Exercise("Yoga Stretch", 90)],
            "Friday": [Exercise("Plank", 60), Exercise("Squats", 45), Exercise("Jump Rope", 90)],
            "Saturday": [Exercise("Jogging", 120), Exercise("Stretching", 90), Exercise("Lunges", 45)],
            "Sunday": [Exercise("Light Walk", 180), Exercise("Meditation", 120)]
        }

        self.total_exercises = sum(len(ex) for ex in self.weekly_plan.values())

        # PROGRESS TRACKER (NEW)
        self.progressTracker = ProgressTracker(self.total_exercises)

        self.load_data()
        self.create_ui()

    # ==========================================
    # SAVE DATA
    # ==========================================
    def save_data(self):
        data = {
            "name": self.user_name.get(),
            "weight": self.user_weight.get(),
            "availability": {day: entry.get() for day, entry in self.availability.items()},
            "completed": self.progressTracker.completed
        }

        with open(self.DATA_FILE, "w") as f:
            json.dump(data, f)

        messagebox.showinfo("Saved", "Information Saved Successfully!")

    # ==========================================
    # LOAD DATA
    # ==========================================
    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as f:
                data = json.load(f)

            self.user_name.set(data.get("name", ""))
            self.user_weight.set(data.get("weight", ""))

            completed = data.get("completed", 0)

            # restore tracker state
            self.progressTracker.completed = completed
            self.progressTracker.calculateProgress()

            self.saved_availability = data.get("availability", {})
        else:
            self.saved_availability = {}

    # ==========================================
    # UI
    # ==========================================
    def create_ui(self):

        header = tk.Frame(self.root, bg=self.primary, height=80)
        header.pack(fill="x")

        tk.Label(
            header,
            text="FITastic Flexie Timer",
            font=("Poppins", 24, "bold"),
            bg=self.primary,
            fg="white"
        ).pack(pady=15)

        container = tk.Frame(self.root, bg=self.bg)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.bg)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.scroll_frame = tk.Frame(canvas, bg=self.bg)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = self.scroll_frame

        left_panel = tk.Frame(main_frame, bg=self.bg)
        left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        right_panel = tk.Frame(main_frame, bg=self.bg)
        right_panel.pack(side="right", fill="y", padx=20, pady=20)

        # ================= USER =================
        user_card = tk.Frame(left_panel, bg=self.light)
        user_card.pack(fill="x", pady=10)

        tk.Label(user_card, text="Name", bg=self.light).pack(anchor="w", padx=20)
        tk.Entry(user_card, textvariable=self.user_name).pack(padx=20, pady=5, fill="x")

        tk.Label(user_card, text="Weight", bg=self.light).pack(anchor="w", padx=20)
        tk.Entry(user_card, textvariable=self.user_weight).pack(padx=20, pady=5, fill="x")

        tk.Button(
            user_card,
            text="Save Information",
            command=self.save_data,
            bg=self.primary,
            fg="white"
        ).pack(padx=20, pady=10, fill="x")

        # ================= WORKOUT =================
        workout_card = tk.Frame(left_panel, bg=self.light)
        workout_card.pack(fill="both", expand=True, pady=10)

        tk.Label(workout_card, text="🏋 Weekly Workout Plan",
                 font=("Poppins", 16, "bold"),
                 bg=self.light).pack(anchor="w", padx=20, pady=10)

        self.exercise_frame = tk.Frame(workout_card, bg=self.light)
        self.exercise_frame.pack(fill="both", padx=20, pady=10)

        self.display_exercises()

        # ================= TIMER =================
        timer_card = tk.Frame(right_panel, bg=self.light, padx=20, pady=20)
        timer_card.pack(fill="x")

        self.timer_label = tk.Label(
            timer_card,
            text="00:00",
            font=("Poppins", 36, "bold"),
            bg=self.light,
            fg=self.primary
        )
        self.timer_label.pack(pady=10)

        tk.Button(
            timer_card,
            text="Stop Timer",
            command=self.stop_timer,
            bg=self.accent,
            fg="white"
        ).pack(pady=10)

        # ================= PROGRESS =================
        progress_card = tk.Frame(right_panel, bg=self.light, padx=20, pady=20)
        progress_card.pack(fill="x", pady=20)

        self.progress = ttk.Progressbar(progress_card, length=250)
        self.progress.pack(pady=10)

        self.progress_label = tk.Label(
            progress_card,
            text=self.progressTracker.displayProgress(),
            bg=self.light
        )
        self.progress_label.pack()

        self.update_progress_ui()

    # ==========================================
    # EXERCISES
    # ==========================================
    def display_exercises(self):
        for widget in self.exercise_frame.winfo_children():
            widget.destroy()

        for day, exercises in self.weekly_plan.items():

            tk.Label(self.exercise_frame,
                     text=day,
                     font=("Arial", 12, "bold"),
                     bg=self.light,
                     fg=self.primary).pack(anchor="w")

            for ex in exercises:
                tk.Button(
                    self.exercise_frame,
                    text=f"{ex.name} ({ex.duration}s)",
                    command=lambda e=ex: self.start_exercise(e),
                    anchor="w"
                ).pack(fill="x", pady=2)

    # ==========================================
    # TIMER LOGIC
    # ==========================================
    def start_exercise(self, exercise):
        self.current_exercise = exercise
        self.time_left = exercise.duration
        messagebox.showinfo("Start", exercise.name)
        self.run_timer()

    def run_timer(self):
        mins = self.time_left // 60
        secs = self.time_left % 60

        self.timer_label.config(text=f"{mins:02}:{secs:02}")

        if self.time_left > 0:
            self.time_left -= 1
            self.after_id = self.root.after(1000, self.run_timer)

        else:
            if self.current_exercise:
                self.progressTracker.markCompleted(self.current_exercise)
                self.update_progress_ui()
                self.save_data()
                messagebox.showinfo("Done", "Exercise Completed!")

    def update_progress_ui(self):
        self.progress["value"] = self.progressTracker.progressRate * 100
        self.progress_label.config(text=self.progressTracker.displayProgress())

    def stop_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.timer_label.config(text="00:00")
        messagebox.showinfo("Stopped", "Timer stopped")


# RUN
root = tk.Tk()
app = FITasticFlexieTimer(root)
root.mainloop()