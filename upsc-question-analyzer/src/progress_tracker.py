import time
import os
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from typing import Dict, Optional
from datetime import datetime

class ProgressTracker:
    def __init__(self, total_questions: int, excel_path: str):
        self.total_questions = total_questions
        self.excel_path = excel_path
        self.processed_count = 0
        self.start_time = time.time()
        self.console = Console()
        
        self.current_question = ""
        self.current_status = "Initializing..."
        self.success_count = 0
        self.error_count = 0
        self.last_error = ""
        
        # Progress bar setup
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeRemainingColumn(),
            console=self.console
        )
        
        self.main_task = self.progress.add_task("Analyzing Questions", total=total_questions)
    
    def update_current_question(self, question_text: str, question_number: int):
        """Update current question being processed"""
        self.current_question = f"Q{question_number}: {question_text[:100]}..."
        self.current_status = f"Processing Question {question_number}/{self.total_questions}"
    
    def mark_success(self):
        """Mark current question as successfully processed"""
        self.processed_count += 1
        self.success_count += 1
        self.progress.update(self.main_task, advance=1)
    
    def mark_error(self, error_msg: str):
        """Mark current question as failed"""
        self.processed_count += 1
        self.error_count += 1
        self.last_error = error_msg
        self.progress.update(self.main_task, advance=1)
    
    def get_stats_table(self) -> Table:
        """Generate statistics table"""
        table = Table(title="Analysis Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green", width=15)
        
        elapsed_time = time.time() - self.start_time
        elapsed_str = f"{int(elapsed_time // 60)}m {int(elapsed_time % 60)}s"
        
        questions_per_min = (self.processed_count / (elapsed_time / 60)) if elapsed_time > 0 else 0
        
        table.add_row("Total Questions", str(self.total_questions))
        table.add_row("Processed", str(self.processed_count))
        table.add_row("Successful", str(self.success_count))
        table.add_row("Errors", str(self.error_count))
        table.add_row("Elapsed Time", elapsed_str)
        table.add_row("Rate", f"{questions_per_min:.1f}/min")
        
        if os.path.exists(self.excel_path):
            file_size = os.path.getsize(self.excel_path)
            size_mb = file_size / (1024 * 1024)
            table.add_row("Excel Size", f"{size_mb:.2f} MB")
        
        return table
    
    def get_current_status_panel(self) -> Panel:
        """Generate current status panel"""
        content = f"""
[bold]Current Status:[/bold] {self.current_status}

[bold]Current Question:[/bold]
{self.current_question}

[bold]Excel Output:[/bold] {self.excel_path}
[dim]Last Updated: {datetime.now().strftime('%H:%M:%S')}[/dim]
"""
        
        if self.last_error:
            content += f"\n[bold red]Last Error:[/bold red]\n{self.last_error}"
        
        return Panel(content, title="Current Processing", border_style="blue")
    
    def create_live_display(self) -> Layout:
        """Create the live display layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", size=10),
            Layout(name="progress", size=3),
            Layout(name="footer", size=5)
        )
        
        layout["header"].update(
            Panel("🎯 UPSC Question Quality Analysis", style="bold green")
        )
        
        layout["main"].split_row(
            Layout(self.get_current_status_panel(), name="status"),
            Layout(self.get_stats_table(), name="stats")
        )
        
        layout["progress"].update(self.progress)
        
        layout["footer"].update(
            Panel(
                "[bold]Instructions:[/bold] The Excel file is being updated in real-time. "
                "You can open it in another window to monitor progress. Press Ctrl+C to stop.",
                style="dim"
            )
        )
        
        return layout
    
    def start_live_display(self):
        """Start the live display"""
        return Live(self.create_live_display(), refresh_per_second=2, console=self.console)
    
    def update_display(self, live_display):
        """Update the live display with current information"""
        try:
            layout = self.create_live_display()
            live_display.update(layout)
        except Exception as e:
            # Fallback to simple console update
            self.console.print(f"Display update error: {e}")
    
    def print_final_summary(self):
        """Print final summary when processing is complete"""
        self.console.print("\n")
        self.console.rule("[bold green]Analysis Complete!")
        
        # Final statistics
        final_stats = Table(title="Final Summary", show_header=True, header_style="bold green")
        final_stats.add_column("Metric", style="cyan")
        final_stats.add_column("Value", style="green")
        
        elapsed_time = time.time() - self.start_time
        elapsed_str = f"{int(elapsed_time // 60)}m {int(elapsed_time % 60)}s"
        
        final_stats.add_row("Total Questions Processed", str(self.processed_count))
        final_stats.add_row("Successful Analyses", str(self.success_count))
        final_stats.add_row("Failed Analyses", str(self.error_count))
        final_stats.add_row("Success Rate", f"{(self.success_count/self.processed_count)*100:.1f}%" if self.processed_count > 0 else "0%")
        final_stats.add_row("Total Time", elapsed_str)
        final_stats.add_row("Excel File", self.excel_path)
        
        self.console.print(final_stats)
        
        if os.path.exists(self.excel_path):
            self.console.print(f"\n✅ [bold green]Excel file saved successfully:[/bold green] {self.excel_path}")
        else:
            self.console.print(f"\n❌ [bold red]Excel file not found:[/bold red] {self.excel_path}")
        
        self.console.print("\n🎉 [bold]Analysis complete! You can now open the Excel file to review the results.[/bold]")

class SimpleProgressTracker:
    """Simplified progress tracker for non-interactive environments"""
    
    def __init__(self, total_questions: int, excel_path: str):
        self.total_questions = total_questions
        self.excel_path = excel_path
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = time.time()
        print(f"Starting analysis of {total_questions} questions...")
    
    def update_current_question(self, question_text: str, question_number: int):
        print(f"\n📝 Processing Question {question_number}/{self.total_questions}")
    
    def mark_success(self):
        self.processed_count += 1
        self.success_count += 1
        print(f"✅ Done")
    
    def mark_error(self, error_msg: str):
        self.processed_count += 1
        self.error_count += 1
        print(f"❌ Failed")
    
    def print_final_summary(self):
        elapsed_time = time.time() - self.start_time
        print(f"\n{'='*50}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*50}")
        print(f"Total Questions: {self.total_questions}")
        print(f"Processed: {self.processed_count}")
        print(f"Successful: {self.success_count}")
        print(f"Failed: {self.error_count}")
        print(f"Success Rate: {(self.success_count/self.processed_count)*100:.1f}%" if self.processed_count > 0 else "0%")
        print(f"Time Taken: {int(elapsed_time // 60)}m {int(elapsed_time % 60)}s")
        print(f"Excel File: {self.excel_path}")
        print(f"{'='*50}")