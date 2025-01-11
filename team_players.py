from psychopy import visual, core, event
import numpy as np
from dataclasses import dataclass
import random
from typing import List, Dict

@dataclass
class CrewMember:
    id: str
    role: str
    expertise: float  # 0-1
    stress_level: float  # 0-1
    fatigue: float  # 0-1
    cooperation: float  # 0-1
    leadership: float  # 0-1
    current_task: str = None
    
class Task:
    def __init__(self, name: str, difficulty: float, required_roles: List[str]):
        self.name = name
        self.difficulty = difficulty  # 0-1
        self.required_roles = required_roles
        self.progress = 0.0
        self.assigned_crew = []
        
class CrewAI:
    def __init__(self, window_size=(800, 600)):
        # Initialize PsychoPy window
        self.win = visual.Window(size=window_size, units='pix')
        
        # Initialize crew members
        self.crew = self.create_crew()
        
        # Initialize tasks
        self.tasks = self.create_tasks()
        
        # Performance metrics
        self.team_performance = 0.0
        self.mission_progress = 0.0
        
        # Create visual elements
        self.setup_visuals()
        
    def create_crew(self) -> List[CrewMember]:
        """Create a diverse crew with different roles and attributes"""
        roles = [
            "Commander", "Pilot", "Engineer", 
            "Science Officer", "Medical Officer"
        ]
        
        crew = []
        for i, role in enumerate(roles):
            crew_member = CrewMember(
                id=f"CM{i+1}",
                role=role,
                expertise=random.uniform(0.7, 1.0),
                stress_level=random.uniform(0.1, 0.3),
                fatigue=random.uniform(0.1, 0.3),
                cooperation=random.uniform(0.7, 1.0),
                leadership=random.uniform(0.6, 1.0) if role == "Commander" else random.uniform(0.4, 0.8)
            )
            crew.append(crew_member)
            
        return crew
    
    def create_tasks(self) -> List[Task]:
        """Create mission tasks"""
        return [
            Task("Navigation", 0.7, ["Commander", "Pilot"]),
            Task("System Maintenance", 0.6, ["Engineer"]),
            Task("Research", 0.5, ["Science Officer"]),
            Task("Health Monitoring", 0.4, ["Medical Officer"]),
            Task("Emergency Response", 0.8, ["Commander", "Medical Officer", "Engineer"])
        ]
    
    def setup_visuals(self):
        """Setup visual elements for simulation display"""
        self.crew_sprites = {}
        positions = [(-300, 200), (-150, 200), (0, 200), (150, 200), (300, 200)]
        
        for crew_member, pos in zip(self.crew, positions):
            # Create crew member visual
            self.crew_sprites[crew_member.id] = {
                'circle': visual.Circle(
                    self.win, 
                    radius=20,
                    pos=pos,
                    fillColor='blue'
                ),
                'text': visual.TextStim(
                    self.win,
                    text=crew_member.role,
                    pos=(pos[0], pos[1]-40),
                    height=12
                ),
                'status': visual.TextStim(
                    self.win,
                    text="",
                    pos=(pos[0], pos[1]-60),
                    height=10,
                    color='white'
                )
            }
        
        # Create task visuals
        self.task_texts = []
        for i, task in enumerate(self.tasks):
            self.task_texts.append(
                visual.TextStim(
                    self.win,
                    text=f"{task.name}: 0%",
                    pos=(-300, -100 - i*30),
                    height=12,
                    alignText='left'
                )
            )
            
        # Create performance meter
        self.performance_meter = visual.Rect(
            self.win,
            width=200,
            height=20,
            pos=(0, -300),
            fillColor='green'
        )
        
        self.performance_text = visual.TextStim(
            self.win,
            text="Team Performance: 0%",
            pos=(0, -250),
            height=15
        )
    
    def update_crew_state(self):
        """Update crew member states based on various factors"""
        for crew_member in self.crew:
            # Update fatigue
            crew_member.fatigue += random.uniform(0.01, 0.03)
            crew_member.fatigue = min(crew_member.fatigue, 1.0)
            
            # Update stress based on task difficulty
            if crew_member.current_task:
                task = next(t for t in self.tasks if t.name == crew_member.current_task)
                crew_member.stress_level += task.difficulty * random.uniform(0.01, 0.02)
                crew_member.stress_level = min(crew_member.stress_level, 1.0)
            
            # Recovery when not assigned to task
            if not crew_member.current_task:
                crew_member.fatigue = max(0, crew_member.fatigue - 0.02)
                crew_member.stress_level = max(0, crew_member.stress_level - 0.02)
    
    def assign_tasks(self):
        """Assign crew members to tasks based on roles and current state"""
        for task in self.tasks:
            # Clear previous assignments
            task.assigned_crew = []
            
            # Find available crew members for this task
            for crew_member in self.crew:
                if (crew_member.role in task.required_roles and 
                    not crew_member.current_task and
                    crew_member.fatigue < 0.8 and
                    crew_member.stress_level < 0.8):
                    
                    task.assigned_crew.append(crew_member)
                    crew_member.current_task = task.name
    
    def update_task_progress(self):
        """Update progress on all active tasks"""
        for task in self.tasks:
            if task.assigned_crew:
                # Calculate collective performance
                performance = sum(
                    cm.expertise * (1 - cm.fatigue) * (1 - cm.stress_level)
                    for cm in task.assigned_crew
                ) / len(task.required_roles)
                
                # Update progress
                task.progress = min(1.0, task.progress + performance * 0.02)
    
    def calculate_team_performance(self):
        """Calculate overall team performance"""
        task_performances = [task.progress for task in self.tasks]
        crew_states = [
            (1 - cm.fatigue) * (1 - cm.stress_level) * cm.cooperation
            for cm in self.crew
        ]
        
        self.team_performance = (
            sum(task_performances) / len(self.tasks) * 0.6 +
            sum(crew_states) / len(self.crew) * 0.4
        )
    
    def update_visuals(self):
        """Update all visual elements"""
        # Update crew visuals
        for crew_member in self.crew:
            sprite = self.crew_sprites[crew_member.id]
            
            # Update color based on stress and fatigue
            stress_color = min(1, crew_member.stress_level)
            sprite['circle'].fillColor = [stress_color, 0, 1-stress_color]
            
            # Update status text
            status = f"Task: {crew_member.current_task or 'None'}\n"
            status += f"Fatigue: {crew_member.fatigue:.2f}"
            sprite['status'].text = status
            
            # Draw elements
            sprite['circle'].draw()
            sprite['text'].draw()
            sprite['status'].draw()
        
        # Update task progress
        for task, text in zip(self.tasks, self.task_texts):
            text.text = f"{task.name}: {task.progress*100:.0f}%"
            text.draw()
        
        # Update performance meter
        self.performance_meter.width = 200 * self.team_performance
        self.performance_meter.draw()
        
        self.performance_text.text = f"Team Performance: {self.team_performance*100:.0f}%"
        self.performance_text.draw()
        
        self.win.flip()
    
    def run_simulation(self, duration=1000):
        """Run the main simulation loop"""
        clock = core.Clock()
        
        while clock.getTime() < duration:
            # Check for exit
            if 'escape' in event.getKeys():
                break
            
            # Update simulation
            self.update_crew_state()
            self.assign_tasks()
            self.update_task_progress()
            self.calculate_team_performance()
            
            # Update display
            self.update_visuals()
            
            # Brief pause
            core.wait(0.1)
        
        self.win.close()

if __name__ == "__main__":
    # Create and run simulation
    sim = CrewAI()
    sim.run_simulation()
