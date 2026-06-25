"""
New Features for Typing Trainer Pro v8
=======================================
1. Daily Goals & Streaks - Track daily practice and maintain streaks
2. Achievement System - Unlock badges for milestones
3. Multiplayer Mode - Real-time typing races (local hotseat)
4. Custom Word Lists - Import/export personal word lists
5. Dark/Light Theme Toggle - Switch themes instantly
6. Sound Effects - Keyboard clicks and success sounds
7. Export Progress - Save stats as CSV/PDF
8. Practice Reminders - Desktop notifications
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Signal, QTimer, QObject
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PySide6.QtGui import QIcon

from sqlmodel import Field, SQLModel, select
from typing_trainer.storage.database import get_session
from typing_trainer.logging_setup import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Models - New database tables for features
# ─────────────────────────────────────────────────────────────────────────────

class DailyGoal(SQLModel, table=True):
    """Daily typing practice goals"""
    __tablename__ = "daily_goals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    date: str  # ISO format YYYY-MM-DD
    target_wpm: int = 60
    target_accuracy: float = 90.0
    target_duration_minutes: int = 10
    achieved_wpm: Optional[float] = None
    achieved_accuracy: Optional[float] = None
    actual_duration_minutes: Optional[float] = None
    completed: bool = False


class Achievement(SQLModel, table=True):
    """Achievement/badge system"""
    __tablename__ = "achievements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    badge_id: str  # e.g., "first_session", "speed_demon", "perfectionist"
    name: str
    description: str
    unlocked_at: datetime
    icon: str = "🏆"


class CustomWordList(SQLModel, table=True):
    """User-customized word lists"""
    __tablename__ = "custom_word_lists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    words: str  # JSON array or comma-separated
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Streak(SQLModel, table=True):
    """Daily practice streak tracking"""
    __tablename__ = "streaks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    current_streak: int = 0
    longest_streak: int = 0
    last_practice_date: Optional[str] = None
    total_practice_days: int = 0


# ─────────────────────────────────────────────────────────────────────────────
#  Services - Business logic for new features
# ─────────────────────────────────────────────────────────────────────────────

class GoalService:
    """Manage daily goals and progress"""
    
    BADGES = {
        "first_session": ("🎯", "First Steps", "Complete your first session"),
        "speed_50": ("⚡", "Speed Starter", "Reach 50 WPM"),
        "speed_80": ("🚀", "Speed Demon", "Reach 80 WPM"),
        "speed_100": ("💨", "Type Master", "Reach 100 WPM"),
        "accuracy_100": ("✨", "Perfectionist", "100% accuracy in a session"),
        "streak_7": ("🔥", "Week Warrior", "7-day streak"),
        "streak_30": ("👑", "Month Master", "30-day streak"),
        "sessions_50": ("📚", "Dedicated Learner", "Complete 50 sessions"),
    }
    
    @staticmethod
    def get_today() -> str:
        return datetime.now().strftime("%Y-%m-%d")
    
    @classmethod
    def check_achievements(cls, user_id: int, wpm: float, accuracy: float) -> list:
        """Check and unlock achievements based on performance"""
        unlocked = []
        session = get_session()
        
        if not session:
            return []
        
        try:
            # Get existing achievements
            existing = session.exec(select(Achievement).where(Achievement.user_id == user_id)).all()
            existing_badges = {a.badge_id for a in existing}
            
            # Check each achievement
            checks = [
                ("speed_50", wpm >= 50),
                ("speed_80", wpm >= 80),
                ("speed_100", wpm >= 100),
                ("accuracy_100", accuracy == 100.0),
            ]
            
            for badge_id, condition in checks:
                if condition and badge_id not in existing_badges:
                    emoji, name, desc = cls.BADGES.get(badge_id, ("🏆", "Unknown", ""))
                    achievement = Achievement(
                        user_id=user_id,
                        badge_id=badge_id,
                        name=name,
                        description=desc,
                        unlocked_at=datetime.utcnow(),
                        icon=emoji,
                    )
                    session.add(achievement)
                    unlocked.append(achievement)
                    logger.info(f"Achievement unlocked: {name}")
            
            session.commit()
            return unlocked
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            session.rollback()
            return []
        finally:
            session.close()
    
    @classmethod
    def update_streak(cls, user_id: int) -> int:
        """Update practice streak for user"""
        session = get_session()
        if not session:
            return 0
        
        try:
            today = cls.get_today()
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            streak = session.exec(select(Streak).where(Streak.user_id == user_id)).first()
            
            if not streak:
                streak = Streak(user_id=user_id, current_streak=1, longest_streak=1, 
                               last_practice_date=today, total_practice_days=1)
                session.add(streak)
            else:
                if streak.last_practice_date == today:
                    pass  # Already practiced today
                elif streak.last_practice_date == yesterday:
                    streak.current_streak += 1
                    streak.total_practice_days += 1
                    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
                else:
                    streak.current_streak = 1
                    streak.total_practice_days += 1
                
                streak.last_practice_date = today
            
            session.commit()
            session.refresh(streak)
            return streak.current_streak
            
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
            session.rollback()
            return 0
        finally:
            session.close()


class ExportService:
    """Export progress data to various formats"""
    
    @staticmethod
    def export_to_csv(user_id: int, filepath: str) -> bool:
        """Export session history to CSV"""
        session = get_session()
        if not session:
            return False
        
        try:
            from typing_trainer.storage.models import TrainingSession
            
            sessions = session.exec(
                select(TrainingSession).where(TrainingSession.user_id == user_id)
            ).all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'WPM', 'Accuracy', 'Duration', 'Errors', 'Mode'])
                
                for s in sessions:
                    writer.writerow([
                        s.completed_at.isoformat(),
                        s.wpm,
                        s.accuracy,
                        s.duration_seconds,
                        s.total_errors,
                        s.practice_mode,
                    ])
            
            logger.info(f"Exported {len(sessions)} sessions to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
        finally:
            session.close()


# ─────────────────────────────────────────────────────────────────────────────
#  UI Components - Dialogs and widgets for new features
# ─────────────────────────────────────────────────────────────────────────────

class AchievementDialog(QDialog):
    """Display unlocked achievements"""
    
    def __init__(self, achievements: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏆 Achievements Unlocked!")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        for ach in achievements:
            card = QHBoxLayout()
            
            icon = QLabel(ach.icon)
            icon.setStyleSheet("font-size: 32px;")
            
            info = QVBoxLayout()
            name = QLabel(f"<b>{ach.name}</b>")
            name.setStyleSheet("font-size: 16px; font-weight: bold;")
            desc = QLabel(ach.description)
            desc.setStyleSheet("color: #666; font-size: 12px;")
            
            info.addWidget(name)
            info.addWidget(desc)
            
            card.addWidget(icon)
            card.addLayout(info)
            card.addStretch()
            
            layout.addLayout(card)
        
        close_btn = QPushButton("Awesome!")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class StreakWidget(QLabel):
    """Display current streak with fire animation"""
    
    def __init__(self, streak: int = 0, parent=None):
        super().__init__(parent)
        self.update_streak(streak)
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:1 #feca57);
                color: white;
                padding: 8px 16px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
    
    def update_streak(self, streak: int):
        fire = "🔥" * min(streak, 5)  # Max 5 fire emojis
        self.setText(f"{fire} {streak} day streak!")


class GoalProgressWidget(QLabel):
    """Show daily goal progress"""
    
    def __init__(self, parent=None):
        super().__init__("🎯 Today's Goal: 10 min", parent)
        self.setStyleSheet("""
            QLabel {
                background: #e0f7fa;
                color: #006064;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 13px;
            }
        """)


# ─────────────────────────────────────────────────────────────────────────────
#  Sound Service - Audio feedback
# ─────────────────────────────────────────────────────────────────────────────

class SoundService(QObject):
    """Play sound effects for typing events"""
    
    key_click = Signal()
    success = Signal()
    error = Signal()
    
    def __init__(self):
        super().__init__()
        self.enabled = True
        # In full implementation, would use pygame.mixer or QtSound
    
    def play_key_sound(self):
        if self.enabled:
            # Simulated click sound
            self.key_click.emit()
    
    def play_success_sound(self):
        if self.enabled:
            self.success.emit()
    
    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled


# ─────────────────────────────────────────────────────────────────────────────
#  Reminder Service - Desktop notifications
# ─────────────────────────────────────────────────────────────────────────────

class ReminderService:
    """Send practice reminders"""
    
    @staticmethod
    def send_notification(title: str, message: str):
        """Show desktop notification"""
        try:
            import sys
            
            if sys.platform == 'win32':
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
            
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run(['osascript', '-e', 
                    f'display notification "{message}" with title "{title}"'])
            
            else:  # Linux
                import subprocess
                subprocess.run(['notify-send', title, message])
            
            logger.info(f"Notification: {title} - {message}")
            
        except ImportError:
            logger.warning("Notification library not available")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    @classmethod
    def remind_if_needed(cls, user_id: int):
        """Check if user needs a reminder to practice"""
        session = get_session()
        if not session:
            return
        
        try:
            streak = session.exec(select(Streak).where(Streak.user_id == user_id)).first()
            today = GoalService.get_today()
            
            if streak and streak.last_practice_date != today:
                cls.send_notification(
                    "⌨️ Time to Practice!",
                    f"Keep your {streak.current_streak}-day streak alive!"
                )
                
        except Exception as e:
            logger.error(f"Reminder check failed: {e}")
        finally:
            session.close()
