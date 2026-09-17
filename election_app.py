from __future__ import annotations

from dataclasses import dataclass, field
import sys
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class Candidate:
    name: str
    party: str
    color: str
    stances: Dict[str, str]


@dataclass(frozen=True)
class TimelineStage:
    stage_id: str
    title: str
    description: str
    action_label: str


@dataclass(frozen=True)
class Translation:
    title: str
    subtitle: str
    language: str
    plain_text: str
    high_contrast: str
    progress: str
    candidates: str
    vote: str
    next_stage: str
    previous_stage: str
    vote_received: str
    stance_prompt: str
    selected: str
    complete: str


CANDIDATES = [
    Candidate(
        name="Maya Patel",
        party="Community First",
        color="#e07a5f",
        stances={
            "housing": "Build more affordable homes near public transport.",
            "healthcare": "Expand neighborhood clinics and preventive care.",
            "climate": "Invest in clean buses and resilient local parks.",
        },
    ),
    Candidate(
        name="Daniel Okafor",
        party="Forward Together",
        color="#3d8b8b",
        stances={
            "housing": "Offer first-time buyers support and speed up permits.",
            "healthcare": "Improve digital access and reduce clinic wait times.",
            "climate": "Support small businesses that adopt clean technology.",
        },
    ),
    Candidate(
        name="Elena Rossi",
        party="Independent Voice",
        color="#c49a45",
        stances={
            "housing": "Protect renters while revitalizing unused buildings.",
            "healthcare": "Fund mobile care teams for underserved communities.",
            "climate": "Set clear emissions goals with public progress reports.",
        },
    ),
]

STAGES = [
    TimelineStage("learn", "Learn", "Understand what is being decided and why it matters.", "Start learning"),
    TimelineStage("compare", "Compare", "See each candidate's position on the issues you care about.", "Compare candidates"),
    TimelineStage("decide", "Decide", "Choose the candidate who best represents your priorities.", "Make a choice"),
    TimelineStage("vote", "Vote", "Review your choice and cast your practice ballot.", "Enter voting booth"),
    TimelineStage("complete", "Complete", "Your practice vote has been received.", "View result"),
]

TRANSLATIONS = {
    "English": Translation(
        "Your vote, made clear", "A calm guide to understanding, comparing, and casting your vote.",
        "Language", "Plain language", "High contrast", "Stage {current} of {total}", "Candidate stances",
        "Cast practice vote", "Next stage", "Previous stage", "Vote received", "What matters to you?",
        "Selected", "Journey complete",
    ),
    "Hindi": Translation(
        "आपका वोट, आसान भाषा में", "समझने, तुलना करने और वोट देने के लिए एक सरल मार्गदर्शिका।",
        "भाषा", "सरल भाषा", "उच्च कंट्रास्ट", "चरण {current} / {total}", "उम्मीदवारों की राय",
        "अभ्यास वोट दें", "अगला चरण", "पिछला चरण", "वोट प्राप्त हुआ", "आपके लिए क्या महत्वपूर्ण है?",
        "चुना गया", "यात्रा पूरी हुई",
    ),
    "Spanish": Translation(
        "Tu voto, más claro", "Una guía tranquila para entender, comparar y votar.",
        "Idioma", "Lenguaje sencillo", "Alto contraste", "Etapa {current} de {total}", "Posturas de candidatos",
        "Emitir voto de práctica", "Siguiente etapa", "Etapa anterior", "Voto recibido", "¿Qué te importa?",
        "Seleccionado", "Recorrido completo",
    ),
}


@dataclass
class VoterContext:
    language: str = "English"
    plain_language: bool = False
    high_contrast: bool = False
    completed_stage_ids: List[str] = field(default_factory=list)
    current_stage_index: int = 0
    selected_candidate: Optional[str] = None

    @property
    def current_stage(self) -> TimelineStage:
        return STAGES[self.current_stage_index]

    def complete_current_stage(self) -> None:
        stage_id = self.current_stage.stage_id
        if stage_id not in self.completed_stage_ids:
            self.completed_stage_ids.append(stage_id)

    def move_to(self, index: int) -> None:
        self.current_stage_index = max(0, min(index, len(STAGES) - 1))


class VoterJourney(tk.Frame):
    """Responsive timeline: horizontal at wider widths and vertical on narrow windows."""

    def __init__(self, master: tk.Misc, context: VoterContext, on_change: Callable[[], None]) -> None:
        super().__init__(master)
        self.context = context
        self.on_change = on_change
        self.stage_buttons: List[tk.Button] = []
        self.bind("<Configure>", lambda _event: self.render())

    def render(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        self.stage_buttons = []
        horizontal = self.winfo_width() >= 720
        for index, stage in enumerate(STAGES):
            if horizontal:
                self.columnconfigure(index, weight=1)
                cell = tk.Frame(self)
                cell.grid(row=0, column=index, sticky="ew", padx=3)
            else:
                self.columnconfigure(0, weight=1)
                cell = tk.Frame(self)
                cell.grid(row=index, column=0, sticky="ew", pady=3)

            status = "✓" if stage.stage_id in self.context.completed_stage_ids else str(index + 1)
            button = tk.Button(
                cell,
                text=status,
                width=3,
                relief=tk.FLAT,
                command=lambda position=index: self.select_stage(position),
            )
            button.pack(side=tk.LEFT if not horizontal else tk.TOP, padx=4)
            self.stage_buttons.append(button)
            tk.Label(cell, text=stage.title, font=("Segoe UI", 10, "bold")).pack(
                side=tk.LEFT if not horizontal else tk.TOP, padx=4
            )
            if not horizontal and index < len(STAGES) - 1:
                tk.Label(cell, text="|", foreground="#8a817c").pack(side=tk.LEFT, padx=15)

    def select_stage(self, index: int) -> None:
        self.context.move_to(index)
        self.on_change()


class ElectionApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.context = VoterContext()
        self.translation = TRANSLATIONS[self.context.language]
        self.title("ClearBallot - Your vote, made clear")
        self.geometry("1080x760")
        self.minsize(620, 620)
        self.configure(bg="#f7f3ee")
        self._build_shell()
        self.refresh()

    def _build_shell(self) -> None:
        self.nav = tk.Frame(self, padx=24, pady=16)
        self.nav.pack(fill=tk.X)
        self.brand = tk.Label(self.nav, text="CLEARBALLOT", font=("Segoe UI", 16, "bold"))
        self.brand.pack(side=tk.LEFT)
        self.controls = tk.Frame(self.nav)
        self.controls.pack(side=tk.RIGHT)
        self.language_var = tk.StringVar(value=self.context.language)
        self.language_menu = ttk.Combobox(self.controls, textvariable=self.language_var, values=list(TRANSLATIONS), width=10, state="readonly")
        self.language_menu.pack(side=tk.LEFT, padx=5)
        self.language_menu.bind("<<ComboboxSelected>>", self.change_language)
        self.plain_var = tk.BooleanVar(value=False)
        self.plain_toggle = tk.Checkbutton(self.controls, text="Plain language", variable=self.plain_var, command=self.toggle_plain)
        self.plain_toggle.pack(side=tk.LEFT, padx=5)
        self.contrast_var = tk.BooleanVar(value=False)
        self.contrast_toggle = tk.Checkbutton(self.controls, text="High contrast", variable=self.contrast_var, command=self.toggle_contrast)
        self.contrast_toggle.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self, maximum=len(STAGES), mode="determinate")
        self.progress.pack(fill=tk.X, padx=24)
        self.progress_label = tk.Label(self, anchor="w", padx=24, pady=5)
        self.progress_label.pack(fill=tk.X)

        self.journey = VoterJourney(self, self.context, self.refresh)
        self.journey.pack(fill=tk.X, padx=24, pady=(8, 20))
        self.content = tk.Frame(self, padx=24, pady=8)
        self.content.pack(fill=tk.BOTH, expand=True)

    def refresh(self) -> None:
        self.translation = TRANSLATIONS[self.context.language]
        self.progress.configure(value=self.context.current_stage_index + 1)
        self.progress_label.configure(text=self.translation.progress.format(current=self.context.current_stage_index + 1, total=len(STAGES)))
        self.journey.render()
        self._refresh_content()
        self._apply_theme()

    def _refresh_content(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        stage = self.context.current_stage
        tk.Label(self.content, text=stage.title.upper(), anchor="w", font=("Segoe UI", 10, "bold")).pack(fill=tk.X)
        tk.Label(self.content, text=self.translation.title, anchor="w", font=("Segoe UI", 30, "bold"), pady=8).pack(fill=tk.X)
        tk.Label(self.content, text=stage.description, anchor="w", justify=tk.LEFT, wraplength=760, font=("Segoe UI", 13)).pack(fill=tk.X, pady=(0, 18))

        if stage.stage_id == "compare":
            self._render_candidates()
        elif stage.stage_id == "decide":
            self._render_decision()
        elif stage.stage_id == "complete":
            tk.Label(self.content, text="✓  " + self.translation.vote_received, font=("Segoe UI", 20, "bold"), pady=24).pack()
        else:
            tk.Button(self.content, text=stage.action_label, command=self.next_stage, padx=16, pady=8).pack(anchor="w")

        footer = tk.Frame(self.content)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=16)
        if self.context.current_stage_index > 0:
            tk.Button(footer, text=self.translation.previous_stage, command=self.previous_stage).pack(side=tk.LEFT)
        if self.context.current_stage_index < len(STAGES) - 1 and stage.stage_id not in ("compare", "decide"):
            tk.Button(footer, text=self.translation.next_stage, command=self.next_stage).pack(side=tk.RIGHT)

    def _render_candidates(self) -> None:
        tk.Label(self.content, text=self.translation.candidates, anchor="w", font=("Segoe UI", 14, "bold")).pack(fill=tk.X, pady=(5, 10))
        for candidate in CANDIDATES:
            card = tk.Frame(self.content, bd=1, relief=tk.SOLID, padx=12, pady=10)
            card.pack(fill=tk.X, pady=4)
            tk.Label(card, text=candidate.name, font=("Segoe UI", 12, "bold"), fg=candidate.color).pack(anchor="w")
            tk.Label(card, text=candidate.party).pack(anchor="w")
            stances = "  |  ".join(candidate.stances.values())
            tk.Label(card, text=stances, justify=tk.LEFT, wraplength=850, anchor="w").pack(anchor="w", pady=(5, 0))
        tk.Button(self.content, text=self.translation.next_stage, command=self.next_stage, padx=16, pady=8).pack(anchor="w", pady=12)

    def _render_decision(self) -> None:
        tk.Label(self.content, text=self.translation.stance_prompt, anchor="w", font=("Segoe UI", 14, "bold")).pack(fill=tk.X, pady=(5, 10))
        self.candidate_var = tk.StringVar(value=self.context.selected_candidate or "")
        for candidate in CANDIDATES:
            tk.Radiobutton(self.content, text=f"{candidate.name} - {candidate.party}", variable=self.candidate_var, value=candidate.name, command=self.select_candidate).pack(anchor="w", pady=3)
        tk.Button(self.content, text=self.translation.next_stage, command=self.next_stage, padx=16, pady=8).pack(anchor="w", pady=15)

    def select_candidate(self) -> None:
        self.context.selected_candidate = self.candidate_var.get()

    def next_stage(self) -> None:
        self.context.complete_current_stage()
        if self.context.current_stage_index < len(STAGES) - 1:
            self.context.move_to(self.context.current_stage_index + 1)
            if self.context.current_stage.stage_id == "vote":
                self.play_vote_beep()
        self.refresh()

    def previous_stage(self) -> None:
        self.context.move_to(self.context.current_stage_index - 1)
        self.refresh()

    def change_language(self, _event: tk.Event) -> None:
        self.context.language = self.language_var.get()
        self.refresh()

    def toggle_plain(self) -> None:
        self.context.plain_language = self.plain_var.get()
        self.refresh()

    def toggle_contrast(self) -> None:
        self.context.high_contrast = self.contrast_var.get()
        self.refresh()

    def _apply_theme(self) -> None:
        background = "#111111" if self.context.high_contrast else "#f7f3ee"
        foreground = "#ffffff" if self.context.high_contrast else "#2b2927"
        accent = "#ffe500" if self.context.high_contrast else "#e07a5f"
        self.configure(bg=background)
        for widget in (self.nav, self.controls, self.content, self.journey, self.progress_label):
            widget.configure(bg=background)
        self.brand.configure(bg=background, fg=accent)
        self.progress_label.configure(bg=background, fg=foreground)
        self._set_widget_colors(self.content, background, foreground, accent)
        self._set_widget_colors(self.journey, background, foreground, accent)

    def _set_widget_colors(self, parent: tk.Misc, background: str, foreground: str, accent: str) -> None:
        for child in parent.winfo_children():
            try:
                child.configure(bg=background, fg=foreground, activebackground=accent, activeforeground="#111111")
            except tk.TclError:
                pass
            self._set_widget_colors(child, background, foreground, accent)

    @staticmethod
    def play_vote_beep() -> None:
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(880, 160)
            else:
                print("\\a", end="", flush=True)
        except (ImportError, RuntimeError):
            print("Vote received")


if __name__ == "__main__":
    ElectionApp().mainloop()
