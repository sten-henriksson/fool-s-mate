#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import sqlite3
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import List, Optional

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


__all__ = ["AgentLogger", "LogLevel", "Monitor"]


class Monitor:
    def __init__(self, tracked_model, logger):
        self.step_durations = []
        self.tracked_model = tracked_model
        self.logger = logger
        if getattr(self.tracked_model, "last_input_token_count", "Not found") != "Not found":
            self.total_input_token_count = 0
            self.total_output_token_count = 0

    def get_total_token_counts(self):
        return {
            "input": self.total_input_token_count,
            "output": self.total_output_token_count,
        }

    def reset(self):
        self.step_durations = []
        self.total_input_token_count = 0
        self.total_output_token_count = 0

    def update_metrics(self, step_log):
        """Update the metrics of the monitor.

        Args:
            step_log ([`MemoryStep`]): Step log to update the monitor with.
        """
        step_duration = step_log.duration
        self.step_durations.append(step_duration)
        console_outputs = f"[Step {len(self.step_durations)}: Duration {step_duration:.2f} seconds"

        if getattr(self.tracked_model, "last_input_token_count", None) is not None:
            self.total_input_token_count += self.tracked_model.last_input_token_count
            self.total_output_token_count += self.tracked_model.last_output_token_count
            console_outputs += (
                f"| Input tokens: {self.total_input_token_count:,} | Output tokens: {self.total_output_token_count:,}"
            )
        console_outputs += "]"
        self.logger.log(Text(console_outputs, style="dim"), level=1)


class LogLevel(IntEnum):
    OFF = -1  # No output
    ERROR = 0  # Only errors
    INFO = 1  # Normal output (default)
    DEBUG = 2  # Detailed output


YELLOW_HEX = "#d4b702"


class SQLiteLogger:
    def __init__(self, db_path: str = "agent_logs.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create a general logs table for other logging needs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    level TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            conn.commit()
            
    def log(self, content: str, level: str, metadata: Optional[dict] = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get the calling function name
            import inspect
            caller = inspect.stack()[1]
            function_name = caller.function
            
            # Create table for this function if it doesn't exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {function_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            
            # Insert into the function-specific table
            cursor.execute(f"""
                INSERT INTO {function_name} (timestamp, content)
                VALUES (?, ?)
            """, (datetime.now().isoformat(), content))
            
            # Also insert into general logs table
            cursor.execute("""
                INSERT INTO logs (timestamp, level, content, metadata)
                VALUES (?, ?, ?, ?)
            """, (datetime.now().isoformat(), level, content, 
                 json.dumps(metadata) if metadata else None))
            conn.commit()

class AgentLogger:
    def __init__(self, level: LogLevel = LogLevel.INFO, db_path: Optional[str] = "agent_logs.db"):
        self.level = level
        self.console = Console()
        self.sqlite_logger = SQLiteLogger(db_path)

    def log(self, *args, level: str | LogLevel = LogLevel.INFO, metadata: Optional[dict] = None, **kwargs) -> None:
        """Logs a message to the console and optionally to SQLite database.

        Args:
            level (LogLevel, optional): Defaults to LogLevel.INFO.
            metadata (dict, optional): Additional metadata to store in the database.
        """
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if level <= self.level:
            content = " ".join(str(arg) for arg in args)
            self.console.print(*args, **kwargs)
            if self.sqlite_logger:
                self.sqlite_logger.log(content, level.name, metadata)

    def log_markdown(self, content: str, title: Optional[str] = None, level=LogLevel.INFO, style=YELLOW_HEX) -> None:
        markdown_content = Syntax(
            content,
            lexer="markdown",
            theme="github-dark",
            word_wrap=True,
        )
        if title:
            self.log(
                Group(
                    Rule(
                        "[bold italic]" + title,
                        align="left",
                        style=style,
                    ),
                    markdown_content,
                ),
                level=level,
                metadata={"type": "markdown", "title": title}
            )
        else:
            self.log(markdown_content, level=level, metadata={"type": "markdown"})

    def log_code(self, title: str, content: str, level: int = LogLevel.INFO) -> None:
        self.log(
            Panel(
                Syntax(
                    content,
                    lexer="python",
                    theme="monokai",
                    word_wrap=True,
                ),
                title="[bold]" + title,
                title_align="left",
                box=box.HORIZONTALS,
            ),
            level=level,
            metadata={"type": "code", "title": title}
        )

    def log_rule(self, title: str, level: int = LogLevel.INFO) -> None:
        self.log(
            Rule(
                "[bold]" + title,
                characters="━",
                style=YELLOW_HEX,
            ),
            level=level,
            metadata={"type": "rule"}
        )

    def log_task(self, content: str, subtitle: str, title: Optional[str] = None, level: int = LogLevel.INFO) -> None:
        self.log(
            Panel(
                f"\n[bold]{content}\n",
                title="[bold]New run" + (f" - {title}" if title else ""),
                subtitle=subtitle,
                border_style=YELLOW_HEX,
                subtitle_align="left",
            ),
            level=level,
            metadata={"type": "task", "title": title, "subtitle": subtitle}
        )

    def log_messages(self, messages: List) -> None:
        messages_as_string = "\n".join([json.dumps(dict(message), indent=4) for message in messages])
        self.log(
            Syntax(
                messages_as_string,
                lexer="markdown",
                theme="github-dark",
                word_wrap=True,
            ),
            metadata={"type": "messages", "count": len(messages)}
        )

    def visualize_agent_tree(self, agent):
        if self.sqlite_logger:
            self.sqlite_logger.log(f"Visualized agent tree for {agent.__class__.__name__}", LogLevel.INFO.name)
        def create_tools_section(tools_dict):
            table = Table(show_header=True, header_style="bold")
            table.add_column("Name", style="#1E90FF")
            table.add_column("Description")
            table.add_column("Arguments")

            for name, tool in tools_dict.items():
                args = [
                    f"{arg_name} (`{info.get('type', 'Any')}`{', optional' if info.get('optional') else ''}): {info.get('description', '')}"
                    for arg_name, info in getattr(tool, "inputs", {}).items()
                ]
                table.add_row(name, getattr(tool, "description", str(tool)), "\n".join(args))

            return Group("🛠️ [italic #1E90FF]Tools:[/italic #1E90FF]", table)

        def get_agent_headline(agent, name: Optional[str] = None):
            name_headline = f"{name} | " if name else ""
            return f"[bold {YELLOW_HEX}]{name_headline}{agent.__class__.__name__} | {agent.model.model_id}"

        def build_agent_tree(parent_tree, agent_obj):
            """Recursively builds the agent tree."""
            parent_tree.add(create_tools_section(agent_obj.tools))

            if agent_obj.managed_agents:
                agents_branch = parent_tree.add("🤖 [italic #1E90FF]Managed agents:")
                for name, managed_agent in agent_obj.managed_agents.items():
                    agent_tree = agents_branch.add(get_agent_headline(managed_agent, name))
                    if managed_agent.__class__.__name__ == "CodeAgent":
                        agent_tree.add(
                            f"✅ [italic #1E90FF]Authorized imports:[/italic #1E90FF] {managed_agent.additional_authorized_imports}"
                        )
                    agent_tree.add(f"📝 [italic #1E90FF]Description:[/italic #1E90FF] {managed_agent.description}")
                    build_agent_tree(agent_tree, managed_agent)

        main_tree = Tree(get_agent_headline(agent))
        if agent.__class__.__name__ == "CodeAgent":
            main_tree.add(
                f"✅ [italic #1E90FF]Authorized imports:[/italic #1E90FF] {agent.additional_authorized_imports}"
            )
        build_agent_tree(main_tree, agent)
        self.console.print(main_tree)
