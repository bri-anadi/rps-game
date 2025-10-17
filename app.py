import tkinter as tk
from tkinter import ttk, messagebox, font
import random
from datetime import datetime, timedelta
import json
import os
import urllib.request
import tempfile

class Challenge:
    def __init__(self, challenge_id, name, description, target, reward_points, challenge_type, difficulty="Normal"):
        self.id = challenge_id
        self.name = name
        self.description = description
        self.target = target
        self.reward_points = reward_points
        self.type = challenge_type
        self.difficulty = difficulty
        self.progress = 0
        self.completed = False
        self.date_assigned = datetime.now().strftime("%Y-%m-%d")

    def update_progress(self, value):
        """Update challenge progress"""
        if not self.completed:
            self.progress = min(self.progress + value, self.target)
            if self.progress >= self.target:
                self.completed = True
                return True
        return False

    def get_progress_percentage(self):
        """Get progress as percentage"""
        return int((self.progress / self.target) * 100) if self.target > 0 else 0

    def to_dict(self):
        """Convert challenge to dictionary for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target': self.target,
            'reward_points': self.reward_points,
            'type': self.type,
            'difficulty': self.difficulty,
            'progress': self.progress,
            'completed': self.completed,
            'date_assigned': self.date_assigned
        }

    @staticmethod
    def from_dict(data):
        """Create challenge from dictionary"""
        challenge = Challenge(
            data['id'],
            data['name'],
            data['description'],
            data['target'],
            data['reward_points'],
            data['type'],
            data.get('difficulty', 'Normal')
        )
        challenge.progress = data.get('progress', 0)
        challenge.completed = data.get('completed', False)
        challenge.date_assigned = data.get('date_assigned', datetime.now().strftime("%Y-%m-%d"))
        return challenge

class RockPaperScissorsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("⚔ Rock Paper Scissors Game")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f23")

        self.player_score = 0
        self.computer_score = 0
        self.draws = 0
        self.total_games = 0
        self.game_history = []
        self.max_history = 10
        self.current_streak = 0
        self.best_streak = 0

        self.timer_running = False
        self.player_time = 300
        self.computer_time = 300
        self.timer_id = None
        self.current_turn = None
        self.time_limit = 300
        self.game_over = False

        self.choices = ["Rock", "Paper", "Scissors"]
        self.choice_symbols = {
            "Rock": "ROCK",
            "Paper": "PAPER",
            "Scissors": "SCISSORS"
        }

        self.difficulty = "Normal"

        self.challenges = []
        self.total_challenge_points = 0
        self.challenge_window = None

        self.custom_font = "Courier New"

        self.load_stats()

        self.setup_ui()
        self.bind_keyboard_shortcuts()

    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for quick play"""
        self.root.bind('r', lambda e: self.play("Rock"))
        self.root.bind('R', lambda e: self.play("Rock"))
        self.root.bind('p', lambda e: self.play("Paper"))
        self.root.bind('P', lambda e: self.play("Paper"))
        self.root.bind('s', lambda e: self.play("Scissors"))
        self.root.bind('S', lambda e: self.play("Scissors"))
        self.root.bind('<Escape>', lambda e: self.reset_game())

    def setup_ui(self):
        self.colors = {
            'bg_primary': '#0f0f23',
            'bg_secondary': '#1a1d29',
            'bg_card': '#252838',
            'accent_primary': '#00ff87',
            'accent_secondary': '#00d4ff',
            'player_color': '#00ff87',
            'cpu_color': '#ff4757',
            'draw_color': '#ffa502',
            'text_primary': '#ffffff',
            'text_secondary': '#8b92a8',
            'text_dim': '#5a5f73'
        }

        self.root.config(bg=self.colors['bg_primary'])

        header_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        header_frame.pack(pady=(10, 5))

        title_label = tk.Label(
            header_frame,
            text="⚔ ROCK PAPER SCISSORS ⚔",
            font=(self.custom_font, 22, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Press R (Rock) • P (Paper) • S (Scissors)",
            font=(self.custom_font, 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_primary']
        )
        subtitle_label.pack(pady=(2, 0))

        timer_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        timer_container.pack(pady=5, padx=40, fill=tk.X)

        timer_frame = tk.Frame(timer_container, bg=self.colors['bg_card'], relief=tk.FLAT, bd=0)
        timer_frame.pack(fill=tk.X, padx=2, pady=2)

        timer_main = tk.Frame(timer_frame, bg=self.colors['bg_card'])
        timer_main.pack(pady=8)

        player_timer_frame = tk.Frame(timer_main, bg=self.colors['player_color'], relief=tk.FLAT, bd=0, padx=30, pady=10)
        player_timer_frame.grid(row=0, column=0, padx=10)

        tk.Label(
            player_timer_frame,
            text="⏱ YOU",
            font=(self.custom_font, 9, "bold"),
            bg=self.colors['player_color'],
            fg=self.colors['bg_primary']
        ).pack()

        self.player_timer_label = tk.Label(
            player_timer_frame,
            text="05:00",
            font=(self.custom_font, 28, "bold"),
            bg=self.colors['player_color'],
            fg=self.colors['bg_primary']
        )
        self.player_timer_label.pack(pady=(3, 0))

        vs_timer_frame = tk.Frame(timer_main, bg=self.colors['bg_card'])
        vs_timer_frame.grid(row=0, column=1, padx=15)

        tk.Label(
            vs_timer_frame,
            text="VS",
            font=(self.custom_font, 16, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['accent_secondary']
        ).pack(pady=20)

        computer_timer_frame = tk.Frame(timer_main, bg=self.colors['cpu_color'], relief=tk.FLAT, bd=0, padx=30, pady=10)
        computer_timer_frame.grid(row=0, column=2, padx=10)

        tk.Label(
            computer_timer_frame,
            text="⏱ CPU",
            font=(self.custom_font, 9, "bold"),
            bg=self.colors['cpu_color'],
            fg=self.colors['text_primary']
        ).pack()

        self.computer_timer_label = tk.Label(
            computer_timer_frame,
            text="05:00",
            font=(self.custom_font, 28, "bold"),
            bg=self.colors['cpu_color'],
            fg=self.colors['text_primary']
        )
        self.computer_timer_label.pack(pady=(3, 0))

        timer_control = tk.Frame(timer_frame, bg=self.colors['bg_card'])
        timer_control.pack(pady=(5, 10))

        self.start_pause_btn = tk.Button(
            timer_control,
            text="▶ START GAME",
            font=(self.custom_font, 11, "bold"),
            bg=self.colors['player_color'],
            fg="#000000",
            command=self.toggle_timer,
            width=14,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=self.colors['accent_primary']
        )
        self.start_pause_btn.pack(side=tk.LEFT, padx=6)

        reset_timer_btn = tk.Button(
            timer_control,
            text="↻ RESET TIMER",
            font=(self.custom_font, 11, "bold"),
            bg=self.colors['cpu_color'],
            fg="#000000",
            command=self.reset_timer,
            width=14,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground='#ff6b7a'
        )
        reset_timer_btn.pack(side=tk.LEFT, padx=6)

        time_limit_btn = tk.Button(
            timer_control,
            text="⏰ 5 MIN",
            font=(self.custom_font, 11, "bold"),
            bg="#ffffff",
            fg="#000000",
            command=self.change_time_limit,
            width=10,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground="#e0e0e0"
        )
        time_limit_btn.pack(side=tk.LEFT, padx=6)
        self.time_limit_btn = time_limit_btn

        stats_container_outer = tk.Frame(self.root, bg=self.colors['bg_primary'])
        stats_container_outer.pack(pady=5, padx=40, fill=tk.X)

        stats_frame = tk.Frame(stats_container_outer, bg=self.colors['bg_card'], relief=tk.FLAT)
        stats_frame.pack(fill=tk.X)

        stats_container = tk.Frame(stats_frame, bg=self.colors['bg_card'])
        stats_container.pack(pady=8)

        win_rate = self.calculate_win_rate()
        win_rate_card = tk.Frame(stats_container, bg=self.colors['bg_secondary'], padx=20, pady=8)
        win_rate_card.grid(row=0, column=0, padx=8)

        tk.Label(
            win_rate_card,
            text="WIN RATE",
            font=(self.custom_font, 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_secondary']
        ).pack()

        self.win_rate_label = tk.Label(
            win_rate_card,
            text=f"{win_rate}%",
            font=(self.custom_font, 16, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_secondary']
        )
        self.win_rate_label.pack()

        streak_card = tk.Frame(stats_container, bg=self.colors['bg_secondary'], padx=20, pady=8)
        streak_card.grid(row=0, column=1, padx=8)

        tk.Label(
            streak_card,
            text="STREAK",
            font=(self.custom_font, 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_secondary']
        ).pack()

        self.streak_label = tk.Label(
            streak_card,
            text=f"{self.current_streak}",
            font=(self.custom_font, 16, "bold"),
            fg=self.colors['player_color'],
            bg=self.colors['bg_secondary']
        )
        self.streak_label.pack()

        best_streak_card = tk.Frame(stats_container, bg=self.colors['bg_secondary'], padx=20, pady=8)
        best_streak_card.grid(row=0, column=2, padx=8)

        tk.Label(
            best_streak_card,
            text="BEST",
            font=(self.custom_font, 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_secondary']
        ).pack()

        self.best_streak_label = tk.Label(
            best_streak_card,
            text=f"{self.best_streak}",
            font=(self.custom_font, 16, "bold"),
            fg=self.colors['draw_color'],
            bg=self.colors['bg_secondary']
        )
        self.best_streak_label.pack()

        score_outer = tk.Frame(self.root, bg=self.colors['bg_primary'])
        score_outer.pack(pady=5, padx=40, fill=tk.X)

        self.score_frame = tk.Frame(score_outer, bg=self.colors['bg_card'], relief=tk.FLAT)
        self.score_frame.pack(fill=tk.X)

        score_container = tk.Frame(self.score_frame, bg=self.colors['bg_card'])
        score_container.pack(pady=10)

        player_frame = tk.Frame(score_container, bg=self.colors['player_color'], padx=30, pady=10, relief=tk.FLAT, bd=0)
        player_frame.grid(row=0, column=0, padx=10)

        tk.Label(player_frame, text="⚡ YOU", font=(self.custom_font, 10, "bold"), bg=self.colors['player_color'], fg=self.colors['bg_primary']).pack()
        self.player_score_label = tk.Label(
            player_frame,
            text="0",
            font=(self.custom_font, 36, "bold"),
            bg=self.colors['player_color'],
            fg=self.colors['bg_primary']
        )
        self.player_score_label.pack(pady=(3, 0))

        draw_frame = tk.Frame(score_container, bg=self.colors['draw_color'], padx=30, pady=10, relief=tk.FLAT, bd=0)
        draw_frame.grid(row=0, column=1, padx=10)

        tk.Label(draw_frame, text="⚖ DRAW", font=(self.custom_font, 10, "bold"), bg=self.colors['draw_color'], fg=self.colors['bg_primary']).pack()
        self.draw_label = tk.Label(
            draw_frame,
            text="0",
            font=(self.custom_font, 36, "bold"),
            bg=self.colors['draw_color'],
            fg=self.colors['bg_primary']
        )
        self.draw_label.pack(pady=(3, 0))

        computer_frame = tk.Frame(score_container, bg=self.colors['cpu_color'], padx=30, pady=10, relief=tk.FLAT, bd=0)
        computer_frame.grid(row=0, column=2, padx=10)

        tk.Label(computer_frame, text="🤖 CPU", font=(self.custom_font, 10, "bold"), bg=self.colors['cpu_color'], fg=self.colors['text_primary']).pack()
        self.computer_score_label = tk.Label(
            computer_frame,
            text="0",
            font=(self.custom_font, 36, "bold"),
            bg=self.colors['cpu_color'],
            fg=self.colors['text_primary']
        )
        self.computer_score_label.pack(pady=(3, 0))

        display_outer = tk.Frame(self.root, bg=self.colors['bg_primary'])
        display_outer.pack(pady=5, padx=40)

        display_frame = tk.Frame(display_outer, bg=self.colors['bg_card'], relief=tk.FLAT, bd=0)
        display_frame.pack()

        display_inner = tk.Frame(display_frame, bg=self.colors['bg_card'])
        display_inner.pack(pady=12, padx=15)

        player_display = tk.Frame(display_inner, bg=self.colors['bg_card'])
        player_display.grid(row=0, column=0, padx=15, pady=8)

        tk.Label(player_display, text="YOU", font=(self.custom_font, 9, "bold"), bg=self.colors['bg_card'], fg=self.colors['text_dim']).pack()
        self.player_choice_label = tk.Label(
            player_display,
            text="❔",
            font=(self.custom_font, 38, "bold"),
            bg=self.colors['bg_secondary'],
            fg=self.colors['player_color'],
            width=7,
            height=2,
            relief=tk.FLAT,
            bd=0
        )
        self.player_choice_label.pack(pady=6)

        vs_frame = tk.Frame(display_inner, bg=self.colors['bg_card'])
        vs_frame.grid(row=0, column=1, padx=12)

        tk.Label(vs_frame, text="⚔\nVS\n⚔", font=(self.custom_font, 14, "bold"), bg=self.colors['bg_card'], fg=self.colors['accent_secondary']).pack(pady=30)

        computer_display = tk.Frame(display_inner, bg=self.colors['bg_card'])
        computer_display.grid(row=0, column=2, padx=15, pady=8)

        tk.Label(computer_display, text="CPU", font=(self.custom_font, 9, "bold"), bg=self.colors['bg_card'], fg=self.colors['text_dim']).pack()
        self.computer_choice_label = tk.Label(
            computer_display,
            text="❔",
            font=(self.custom_font, 38, "bold"),
            bg=self.colors['bg_secondary'],
            fg=self.colors['cpu_color'],
            width=7,
            height=2,
            relief=tk.FLAT,
            bd=0
        )
        self.computer_choice_label.pack(pady=6)

        self.result_label = tk.Label(
            self.root,
            text="⚡ Choose your weapon! ⚡",
            font=(self.custom_font, 14, "bold"),
            bg=self.colors['bg_primary'],
            fg=self.colors['accent_secondary'],
            pady=8
        )
        self.result_label.pack(pady=(3, 6))

        button_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        button_frame.pack(pady=8)

        button_style = {
            "font": (self.custom_font, 12, "bold"),
            "width": 15,
            "height": 2,
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2"
        }

        rock_btn = tk.Button(
            button_frame,
            text="🪨 [R] ROCK",
            bg="#6c5ce7",
            fg="#000000",
            command=lambda: self.play("Rock"),
            activebackground="#5f4dd1",
            **button_style
        )
        rock_btn.grid(row=0, column=0, padx=10)
        rock_btn.bind("<Enter>", lambda e: rock_btn.config(bg="#5f4dd1"))
        rock_btn.bind("<Leave>", lambda e: rock_btn.config(bg="#6c5ce7"))

        paper_btn = tk.Button(
            button_frame,
            text="📄 [P] PAPER",
            bg="#0984e3",
            fg="#000000",
            command=lambda: self.play("Paper"),
            activebackground="#0770c7",
            **button_style
        )
        paper_btn.grid(row=0, column=1, padx=10)
        paper_btn.bind("<Enter>", lambda e: paper_btn.config(bg="#0770c7"))
        paper_btn.bind("<Leave>", lambda e: paper_btn.config(bg="#0984e3"))

        scissors_btn = tk.Button(
            button_frame,
            text="✂️ [S] SCISSORS",
            bg="#d63031",
            fg="#000000",
            command=lambda: self.play("Scissors"),
            activebackground="#c02829",
            **button_style
        )
        scissors_btn.grid(row=0, column=2, padx=10)
        scissors_btn.bind("<Enter>", lambda e: scissors_btn.config(bg="#c02829"))
        scissors_btn.bind("<Leave>", lambda e: scissors_btn.config(bg="#d63031"))

        control_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        control_frame.pack(pady=(3, 10))

        control_style = {
            "font": (self.custom_font, 10, "bold"),
            "width": 18,
            "cursor": "hand2",
            "relief": tk.FLAT,
            "bd": 0
        }

        reset_btn = tk.Button(
            control_frame,
            text="↻ [ESC] Reset",
            bg="#ffffff",
            fg="#000000",
            command=self.reset_game,
            activebackground="#e0e0e0",
            **control_style
        )
        reset_btn.grid(row=0, column=0, padx=6)

        history_btn = tk.Button(
            control_frame,
            text="📊 History",
            bg="#ffffff",
            fg="#000000",
            command=self.show_history,
            activebackground="#e0e0e0",
            **control_style
        )
        history_btn.grid(row=0, column=1, padx=6)

        difficulty_btn = tk.Button(
            control_frame,
            text=f"🎯 Difficulty: {self.difficulty}",
            bg="#ffffff",
            fg="#000000",
            command=self.change_difficulty,
            width=22,
            activebackground="#e0e0e0",
            **{k:v for k,v in control_style.items() if k != 'width'}
        )
        difficulty_btn.grid(row=0, column=2, padx=5)
        self.difficulty_btn = difficulty_btn

        challenges_btn = tk.Button(
            control_frame,
            text="🏆 Challenges",
            bg="#ffffff",
            fg="#000000",
            command=self.show_challenges,
            width=20,
            activebackground="#e0e0e0",
            **{k:v for k,v in control_style.items() if k != 'width'}
        )
        challenges_btn.grid(row=0, column=3, padx=6)
        self.challenges_btn = challenges_btn

    def calculate_win_rate(self):
        """Calculate player's win rate"""
        if self.total_games == 0:
            return 0
        return round((self.player_score / self.total_games) * 100, 1)

    def update_statistics(self):
        """Update statistics display"""
        win_rate = self.calculate_win_rate()
        self.win_rate_label.config(text=f"{win_rate}%")
        self.streak_label.config(text=f"{self.current_streak}")
        self.best_streak_label.config(text=f"{self.best_streak}")

    def toggle_timer(self):
        """Start or pause the chess-style timer"""
        if self.game_over:
            messagebox.showinfo("Game Over", "Please reset the timer to start a new game!")
            return

        if self.timer_running:
            self.timer_running = False
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.start_pause_btn.config(text="▶ RESUME", bg=self.colors['draw_color'])
        else:
            self.timer_running = True
            if self.current_turn is None:
                self.current_turn = 'player'
            self.start_pause_btn.config(text="⏸ PAUSE", bg=self.colors['draw_color'])
            self.update_timer()

    def update_timer(self):
        """Update chess-style timer - decrements current player's time"""
        if self.timer_running and not self.game_over:
            if self.current_turn == 'player':
                self.player_time -= 1
                if self.player_time <= 0:
                    self.player_time = 0
                    self.game_over = True
                    self.timer_running = False
                    self.handle_timeout('player')
                    return
            elif self.current_turn == 'computer':
                self.computer_time -= 1
                if self.computer_time <= 0:
                    self.computer_time = 0
                    self.game_over = True
                    self.timer_running = False
                    self.handle_timeout('computer')
                    return

            self.update_timer_display()
            self.timer_id = self.root.after(1000, self.update_timer)

    def update_timer_display(self):
        """Update timer labels"""
        p_minutes = self.player_time // 60
        p_seconds = self.player_time % 60
        player_time_str = f"{p_minutes:02d}:{p_seconds:02d}"
        self.player_timer_label.config(text=player_time_str)

        c_minutes = self.computer_time // 60
        c_seconds = self.computer_time % 60
        computer_time_str = f"{c_minutes:02d}:{c_seconds:02d}"
        self.computer_timer_label.config(text=computer_time_str)

        if self.current_turn == 'player' and self.player_time <= 10:
            color = "#ff0000" if self.player_time % 2 == 0 else "#3ae374"
            self.player_timer_label.config(fg=color)
        elif self.current_turn == 'computer' and self.computer_time <= 10:
            color = "#ff0000" if self.computer_time % 2 == 0 else "white"
            self.computer_timer_label.config(fg=color)

    def switch_turn(self):
        """Switch timer between player and computer"""
        if self.timer_running:
            self.current_turn = 'computer' if self.current_turn == 'player' else 'player'

    def handle_timeout(self, who_timed_out):
        """Handle when a player runs out of time"""
        if who_timed_out == 'player':
            messagebox.showwarning(
                "Time's Up!",
                "You ran out of time!\nComputer wins by timeout!"
            )
            self.computer_score += 3
        else:
            messagebox.showinfo(
                "Time's Up!",
                "Computer ran out of time!\nYou win by timeout!"
            )
            self.player_score += 3

        self.update_score_display()
        self.start_pause_btn.config(text="▶ START GAME", bg=self.colors['player_color'])

    def reset_timer(self):
        """Reset chess timer to initial time"""
        if self.timer_running:
            self.timer_running = False
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

        self.player_time = self.time_limit
        self.computer_time = self.time_limit
        self.current_turn = None
        self.game_over = False

        self.player_timer_label.config(fg=self.colors['bg_primary'])
        self.computer_timer_label.config(fg=self.colors['text_primary'])

        self.update_timer_display()
        self.start_pause_btn.config(text="▶ START GAME", bg=self.colors['player_color'])

    def change_time_limit(self):
        """Change time limit for both players"""
        time_options = [60, 180, 300, 600, 900]
        time_labels = ["⏰ 1 MIN", "⏰ 3 MIN", "⏰ 5 MIN", "⏰ 10 MIN", "⏰ 15 MIN"]

        current_index = time_options.index(self.time_limit) if self.time_limit in time_options else 2
        next_index = (current_index + 1) % len(time_options)

        self.time_limit = time_options[next_index]
        self.time_limit_btn.config(text=time_labels[next_index])

        if not self.timer_running:
            self.player_time = self.time_limit
            self.computer_time = self.time_limit
            self.update_timer_display()

    def get_computer_choice(self):
        """Get computer choice based on difficulty with improved AI"""
        if self.difficulty == "Easy":
            if len(self.game_history) > 0:
                last_player = self.game_history[-1]["player"]
                if random.random() < 0.5:
                    losing_to = {
                        "Rock": "Scissors",
                        "Paper": "Rock",
                        "Scissors": "Paper"
                    }
                    return [k for k, v in losing_to.items() if v == last_player][0]
            return random.choice(self.choices)

        elif self.difficulty == "Hard":
            if len(self.game_history) >= 3:
                recent = [h["player"] for h in self.game_history[-5:]]

                if len(recent) >= 3:
                    if recent[-1] == "Rock" and recent[-2] == "Scissors" and recent[-3] == "Paper":
                        return "Paper"

                most_common = max(set(recent), key=recent.count)

                if random.random() < 0.8:
                    counters = {
                        "Rock": "Paper",
                        "Paper": "Scissors",
                        "Scissors": "Rock"
                    }
                    return counters[most_common]
            return random.choice(self.choices)

        elif self.difficulty == "Expert":
            if len(self.game_history) >= 2:
                recent = [h["player"] for h in self.game_history[-10:]]

                if len(recent) >= 3:
                    if recent[-1] != recent[-2] and recent[-2] != recent[-3]:
                        not_used = [c for c in self.choices if c not in [recent[-1], recent[-2]]]
                        if not_used and random.random() < 0.9:
                            counters = {
                                "Rock": "Paper",
                                "Paper": "Scissors",
                                "Scissors": "Rock"
                            }
                            return counters[not_used[0]]

                most_common = max(set(recent), key=recent.count)
                counters = {
                    "Rock": "Paper",
                    "Paper": "Scissors",
                    "Scissors": "Rock"
                }
                return counters[most_common]
            return random.choice(self.choices)

        else:
            return random.choice(self.choices)

    def determine_winner(self, player_choice, computer_choice):
        """Determine the winner"""
        if player_choice == computer_choice:
            return "Draw"

        winning_combinations = {
            "Rock": "Scissors",
            "Paper": "Rock",
            "Scissors": "Paper"
        }

        if winning_combinations[player_choice] == computer_choice:
            return "Player"
        else:
            return "Computer"

    def play(self, player_choice):
        """Main game logic with enhanced feedback and timer integration"""
        if self.game_over:
            messagebox.showwarning("Game Over", "Timer has expired! Please reset to play again.")
            return

        if not self.timer_running and self.current_turn is None:
            self.toggle_timer()

        if self.timer_running and self.current_turn == 'player':
            self.switch_turn()

        self.result_label.config(text="🤔 Computer is thinking...", fg=self.colors['draw_color'])
        self.root.update()

        thinking_times = {
            "Easy": 500,
            "Normal": 800,
            "Hard": 1200,
            "Expert": 1500
        }
        think_time = thinking_times.get(self.difficulty, 800)

        self.root.after(think_time, lambda: self.computer_responds(player_choice))

    def computer_responds(self, player_choice):
        """Computer makes its choice after thinking time"""
        computer_choice = self.get_computer_choice()

        self.animate_choice_reveal(player_choice, computer_choice)

        winner = self.determine_winner(player_choice, computer_choice)

        self.total_games += 1

        if winner == "Player":
            self.player_score += 1
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
            self.result_label.config(text="🎉 YOU WIN! 🎉", fg=self.colors['player_color'])
            self.animate_winner("player")
        elif winner == "Computer":
            self.computer_score += 1
            self.current_streak = 0
            self.result_label.config(text="💀 COMPUTER WINS! 💀", fg=self.colors['cpu_color'])
            self.animate_winner("computer")
        else:
            self.draws += 1
            self.result_label.config(text="⚖️ IT'S A DRAW! ⚖️", fg=self.colors['draw_color'])

        if self.timer_running:
            self.switch_turn()

        self.update_challenges(player_choice, winner)

        self.update_score_display()
        self.update_statistics()

        self.game_history.append({
            "player": player_choice,
            "computer": computer_choice,
            "winner": winner,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        if len(self.game_history) > self.max_history:
            self.game_history.pop(0)

        self.save_stats()

    def animate_choice_reveal(self, player_choice, computer_choice):
        """Animate the reveal of choices"""
        countdown = ["3", "2", "1", "GO!"]

        def show_countdown(index=0):
            if index < len(countdown):
                self.player_choice_label.config(text=countdown[index])
                self.computer_choice_label.config(text=countdown[index])
                self.root.after(300, show_countdown, index + 1)
            else:
                self.player_choice_label.config(text=self.choice_symbols[player_choice])
                self.computer_choice_label.config(text=self.choice_symbols[computer_choice])

        show_countdown()

    def animate_winner(self, winner):
        """Enhanced animation for winner"""
        if winner == "player":
            label = self.player_choice_label
            colors = [self.colors['player_color'], self.colors['accent_primary'],
                     self.colors['player_color'], self.colors['accent_primary'],
                     self.colors['player_color'], self.colors['bg_secondary']]
        else:
            label = self.computer_choice_label
            colors = [self.colors['cpu_color'], '#ff6b7a',
                     self.colors['cpu_color'], '#ff6b7a',
                     self.colors['cpu_color'], self.colors['bg_secondary']]

        def animate(index=0):
            if index < len(colors):
                label.config(bg=colors[index])
                self.root.after(150, animate, index + 1)
            else:
                label.config(bg=self.colors['bg_secondary'])

        animate()

    def update_score_display(self):
        """Update score labels"""
        self.player_score_label.config(text=str(self.player_score))
        self.computer_score_label.config(text=str(self.computer_score))
        self.draw_label.config(text=str(self.draws))

    def reset_game(self):
        """Reset the game"""
        if self.total_games == 0 or messagebox.askyesno("Reset Game", "Are you sure you want to reset all statistics?"):
            self.player_score = 0
            self.computer_score = 0
            self.draws = 0
            self.total_games = 0
            self.game_history = []
            self.current_streak = 0

            self.update_score_display()
            self.update_statistics()
            self.player_choice_label.config(text="❔", bg=self.colors['bg_secondary'])
            self.computer_choice_label.config(text="❔", bg=self.colors['bg_secondary'])
            self.result_label.config(text="⚡ Choose your weapon! ⚡", fg=self.colors['accent_secondary'])

            self.save_stats()

    def show_history(self):
        """Show enhanced game history"""
        if not self.game_history:
            messagebox.showinfo("Game History", "No games played yet!")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("📊 Game History")
        history_window.geometry("600x450")
        history_window.configure(bg=self.colors['bg_primary'])

        tk.Label(
            history_window,
            text="📊 GAME HISTORY - Last 10 Games",
            font=(self.custom_font, 18, "bold"),
            bg=self.colors['bg_primary'],
            fg=self.colors['accent_secondary']
        ).pack(pady=15)

        container = tk.Frame(history_window, bg=self.colors['bg_primary'])
        container.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=self.colors['bg_card'])
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_card'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        headers = ["⏰ Time", "👤 You", "🤖 Computer", "🏆 Result"]
        for i, header in enumerate(headers):
            tk.Label(
                scrollable_frame,
                text=header,
                font=(self.custom_font, 11, "bold"),
                bg=self.colors['bg_secondary'],
                fg=self.colors['accent_secondary'],
                width=15
            ).grid(row=0, column=i, padx=5, pady=8, sticky="ew")

        for idx, game in enumerate(reversed(self.game_history)):
            bg_color = self.colors['player_color'] if game["winner"] == "Player" else self.colors['cpu_color'] if game["winner"] == "Computer" else self.colors['draw_color']
            row_bg = self.colors['bg_secondary'] if idx % 2 == 0 else self.colors['bg_card']

            tk.Label(scrollable_frame, text=game["timestamp"], bg=row_bg, fg=self.colors['text_secondary'], width=15, font=(self.custom_font, 9)).grid(row=idx+1, column=0, padx=5, pady=2)
            tk.Label(scrollable_frame, text=game["player"], bg=row_bg, fg=self.colors['text_primary'], width=15, font=(self.custom_font, 9)).grid(row=idx+1, column=1, padx=5, pady=2)
            tk.Label(scrollable_frame, text=game["computer"], bg=row_bg, fg=self.colors['text_primary'], width=15, font=(self.custom_font, 9)).grid(row=idx+1, column=2, padx=5, pady=2)
            tk.Label(scrollable_frame, text=game["winner"], bg=bg_color, fg=self.colors['bg_primary'], width=15, font=(self.custom_font, 9, "bold")).grid(row=idx+1, column=3, padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_challenges(self):
        """Display challenges window"""
        if self.challenge_window and tk.Toplevel.winfo_exists(self.challenge_window):
            self.challenge_window.focus()
            return

        self.challenge_window = tk.Toplevel(self.root)
        self.challenge_window.title("🏆 Daily Challenges")
        self.challenge_window.geometry("750x650")
        self.challenge_window.configure(bg=self.colors['bg_primary'])

        title_label = tk.Label(
            self.challenge_window,
            text="🏆 DAILY CHALLENGES 🏆",
            font=(self.custom_font, 24, "bold"),
            fg=self.colors['accent_secondary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=20)

        points_frame = tk.Frame(self.challenge_window, bg=self.colors['bg_card'], relief=tk.FLAT, bd=0)
        points_frame.pack(pady=10, padx=40, fill=tk.X)

        tk.Label(
            points_frame,
            text="TOTAL POINTS",
            font=(self.custom_font, 10, "bold"),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(pady=(12, 2))

        tk.Label(
            points_frame,
            text=f"⭐ {self.total_challenge_points}",
            font=(self.custom_font, 28, "bold"),
            fg=self.colors['draw_color'],
            bg=self.colors['bg_card']
        ).pack(pady=(0, 12))

        challenges_container = tk.Frame(self.challenge_window, bg=self.colors['bg_primary'])
        challenges_container.pack(pady=15, padx=40, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(challenges_container, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(challenges_container, orient="vertical", command=canvas.yview)
        challenges_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])

        challenges_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=challenges_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, challenge in enumerate(self.challenges):
            self.create_challenge_card(challenges_frame, challenge, idx)

        refresh_btn = tk.Button(
            self.challenge_window,
            text="↻ REFRESH CHALLENGES",
            font=(self.custom_font, 11, "bold"),
            bg=self.colors['accent_primary'],
            fg=self.colors['bg_primary'],
            command=self.refresh_challenges_display,
            width=25,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=self.colors['player_color']
        )
        refresh_btn.pack(pady=12)

        today = datetime.now().strftime("%Y-%m-%d")
        info_label = tk.Label(
            self.challenge_window,
            text=f"📅 Challenges reset daily • Today: {today}",
            font=(self.custom_font, 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_primary']
        )
        info_label.pack(pady=(0, 15))

    def create_challenge_card(self, parent, challenge, idx):
        """Create a challenge card widget - Modern design"""
        card_bg = self.colors['bg_secondary'] if challenge.completed else self.colors['bg_card']
        card_frame = tk.Frame(parent, bg=card_bg, relief=tk.FLAT, bd=0)
        card_frame.pack(pady=8, fill=tk.X)

        inner_frame = tk.Frame(card_frame, bg=card_bg)
        inner_frame.pack(pady=15, padx=20, fill=tk.X)

        header_frame = tk.Frame(inner_frame, bg=card_bg)
        header_frame.pack(fill=tk.X, pady=(0, 8))

        name_frame = tk.Frame(header_frame, bg=card_bg)
        name_frame.pack(side=tk.LEFT)

        challenge_icons = {
            "wins": "🎯",
            "streak": "🔥",
            "games": "🎮",
            "specific_choice": "⭐",
            "difficulty": "💪",
            "speed": "⚡"
        }
        icon = challenge_icons.get(challenge.type, "🏆")

        tk.Label(
            name_frame,
            text=f"{icon} {challenge.name}",
            font=(self.custom_font, 13, "bold"),
            fg=self.colors['player_color'] if challenge.completed else self.colors['accent_secondary'],
            bg=card_bg
        ).pack(side=tk.LEFT)

        if challenge.completed:
            tk.Label(
                header_frame,
                text="✓ DONE",
                font=(self.custom_font, 10, "bold"),
                fg=self.colors['player_color'],
                bg=card_bg,
                padx=10,
                pady=2
            ).pack(side=tk.RIGHT)

        tk.Label(
            inner_frame,
            text=challenge.description,
            font=(self.custom_font, 10),
            fg=self.colors['text_secondary'],
            bg=card_bg
        ).pack(anchor=tk.W, pady=(0, 10))

        progress_container = tk.Frame(inner_frame, bg=card_bg)
        progress_container.pack(fill=tk.X, pady=(0, 8))

        progress_bg = tk.Canvas(progress_container, height=12, bg=self.colors['bg_primary'], highlightthickness=0)
        progress_bg.pack(side=tk.LEFT, fill=tk.X, expand=True)

        progress_percent = challenge.get_progress_percentage()
        bar_width = int(progress_bg.winfo_reqwidth() * progress_percent / 100) if progress_percent > 0 else 0

        def update_progress_bar(event=None):
            progress_bg.delete("all")
            canvas_width = progress_bg.winfo_width()
            fill_width = int(canvas_width * progress_percent / 100)

            bar_color = self.colors['player_color'] if challenge.completed else self.colors['accent_primary']
            progress_bg.create_rectangle(0, 0, fill_width, 12, fill=bar_color, outline="")

        progress_bg.bind("<Configure>", update_progress_bar)
        progress_bg.after(10, update_progress_bar)

        progress_text = f"{challenge.progress}/{challenge.target}"
        tk.Label(
            progress_container,
            text=progress_text,
            font=(self.custom_font, 10, "bold"),
            fg=self.colors['text_primary'],
            bg=card_bg
        ).pack(side=tk.LEFT, padx=(12, 0))

        reward_frame = tk.Frame(inner_frame, bg=card_bg)
        reward_frame.pack(fill=tk.X)

        tk.Label(
            reward_frame,
            text=f"💰 Reward: {challenge.reward_points} pts",
            font=(self.custom_font, 9, "bold"),
            fg=self.colors['draw_color'],
            bg=card_bg
        ).pack(side=tk.LEFT)

    def refresh_challenges_display(self):
        """Refresh the challenges display"""
        if self.challenge_window and tk.Toplevel.winfo_exists(self.challenge_window):
            self.challenge_window.destroy()
        self.show_challenges()

    def update_challenges(self, player_choice, winner):
        """Update challenge progress based on game results"""
        completed_challenges = []

        for challenge in self.challenges:
            if challenge.completed:
                continue

            updated = False

            if challenge.type == "wins" and winner == "Player":
                updated = challenge.update_progress(1)

            elif challenge.type == "streak":
                if self.current_streak >= challenge.target:
                    challenge.progress = challenge.target
                    updated = challenge.update_progress(0)

            elif challenge.type == "games":
                updated = challenge.update_progress(1)

            elif challenge.type == "specific_choice":
                if winner == "Player" and player_choice == challenge.difficulty:
                    updated = challenge.update_progress(1)

            elif challenge.type == "difficulty":
                if winner == "Player" and self.difficulty == challenge.difficulty:
                    updated = challenge.update_progress(1)

            elif challenge.type == "speed":
                if winner == "Player":
                    updated = challenge.update_progress(1)

            if updated:
                completed_challenges.append(challenge)

        if completed_challenges:
            self.show_challenge_completion(completed_challenges)

        self.save_stats()

    def show_challenge_completion(self, completed_challenges):
        """Show notification for completed challenges"""
        for challenge in completed_challenges:
            self.total_challenge_points += challenge.reward_points

            notification = tk.Toplevel(self.root)
            notification.title("Challenge Completed!")
            notification.geometry("400x250")
            notification.configure(bg="#1a1a2e")

            notification.update_idletasks()
            x = (notification.winfo_screenwidth() // 2) - 200
            y = (notification.winfo_screenheight() // 2) - 125
            notification.geometry(f"400x250+{x}+{y}")

            tk.Label(
                notification,
                text="CHALLENGE COMPLETED!",
                font=(self.custom_font, 18, "bold"),
                fg="#3ae374",
                bg="#1a1a2e"
            ).pack(pady=20)

            tk.Label(
                notification,
                text=challenge.name,
                font=(self.custom_font, 14, "bold"),
                fg="#00d2ff",
                bg="#1a1a2e"
            ).pack(pady=10)

            tk.Label(
                notification,
                text=challenge.description,
                font=(self.custom_font, 11),
                fg="#ecf0f1",
                bg="#1a1a2e"
            ).pack(pady=5)

            tk.Label(
                notification,
                text=f"+{challenge.reward_points} Points!",
                font=(self.custom_font, 16, "bold"),
                fg="#f39c12",
                bg="#1a1a2e"
            ).pack(pady=15)

            tk.Button(
                notification,
                text="AWESOME!",
                font=(self.custom_font, 12, "bold"),
                bg="#9b59b6",
                fg="white",
                command=notification.destroy,
                width=15,
                cursor="hand2"
            ).pack(pady=10)

            notification.after(5000, notification.destroy)

        if self.challenge_window and tk.Toplevel.winfo_exists(self.challenge_window):
            self.refresh_challenges_display()

    def change_difficulty(self):
        """Change difficulty level with Expert mode"""
        difficulties = ["Easy", "Normal", "Hard", "Expert"]
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]

        self.difficulty_btn.config(text=f"🎯 Difficulty: {self.difficulty}")

        descriptions = {
            "Easy": "Computer makes random moves with occasional mistakes",
            "Normal": "Computer plays completely random",
            "Hard": "Computer analyzes your patterns and tries to counter",
            "Expert": "Advanced AI with pattern recognition - Very challenging!"
        }

        messagebox.showinfo(
            "Difficulty Changed",
            f"Difficulty: {self.difficulty}\n\n{descriptions[self.difficulty]}"
        )

    def save_stats(self):
        """Save game statistics to file"""
        stats = {
            "player_score": self.player_score,
            "computer_score": self.computer_score,
            "draws": self.draws,
            "total_games": self.total_games,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "history": self.game_history,
            "total_challenge_points": self.total_challenge_points,
            "challenges": [c.to_dict() for c in self.challenges],
            "last_challenge_date": datetime.now().strftime("%Y-%m-%d")
        }

        try:
            with open("rps_stats.json", "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=4)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def generate_daily_challenges(self):
        """Generate random daily challenges"""
        challenge_pool = [
            Challenge("win_3", "Quick Winner", "Win 3 games", 3, 50, "wins"),
            Challenge("win_5", "Victory March", "Win 5 games", 5, 100, "wins"),
            Challenge("win_10", "Dominator", "Win 10 games", 10, 250, "wins"),

            Challenge("streak_3", "Hot Streak", "Win 3 games in a row", 3, 75, "streak"),
            Challenge("streak_5", "Unstoppable", "Win 5 games in a row", 5, 150, "streak"),

            Challenge("games_10", "Practice Makes Perfect", "Play 10 games", 10, 50, "games"),
            Challenge("games_20", "Marathon Player", "Play 20 games", 20, 100, "games"),

            Challenge("rock_wins", "Rock Solid", "Win 5 games using Rock", 5, 100, "specific_choice", "Rock"),
            Challenge("paper_wins", "Paper Champion", "Win 5 games using Paper", 5, 100, "specific_choice", "Paper"),
            Challenge("scissors_wins", "Scissors Master", "Win 5 games using Scissors", 5, 100, "specific_choice", "Scissors"),

            Challenge("beat_hard", "Hard Mode Hero", "Win 3 games on Hard difficulty", 3, 150, "difficulty", "Hard"),
            Challenge("beat_expert", "Expert Slayer", "Win 3 games on Expert difficulty", 3, 200, "difficulty", "Expert"),

            Challenge("quick_5", "Speed Demon", "Win 5 games in under 5 minutes total", 5, 150, "speed"),
        ]

        selected = random.sample(challenge_pool, min(3, len(challenge_pool)))
        return selected

    def load_stats(self):
        """Load game statistics from file"""
        if os.path.exists("rps_stats.json"):
            try:
                with open("rps_stats.json", "r", encoding="utf-8") as f:
                    stats = json.load(f)
                    self.player_score = stats.get("player_score", 0)
                    self.computer_score = stats.get("computer_score", 0)
                    self.draws = stats.get("draws", 0)
                    self.total_games = stats.get("total_games", 0)
                    self.current_streak = stats.get("current_streak", 0)
                    self.best_streak = stats.get("best_streak", 0)
                    self.game_history = stats.get("history", [])
                    self.total_challenge_points = stats.get("total_challenge_points", 0)

                    challenges_data = stats.get("challenges", [])
                    last_challenge_date = stats.get("last_challenge_date", "")
                    today = datetime.now().strftime("%Y-%m-%d")

                    if last_challenge_date != today:
                        self.challenges = self.generate_daily_challenges()
                    else:
                        self.challenges = [Challenge.from_dict(c) for c in challenges_data]

                    if not self.challenges:
                        self.challenges = self.generate_daily_challenges()
            except Exception as e:
                print(f"Error loading stats: {e}")
                if not self.challenges:
                    self.challenges = self.generate_daily_challenges()
        else:
            self.challenges = self.generate_daily_challenges()

def main():
    root = tk.Tk()
    game = RockPaperScissorsGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
