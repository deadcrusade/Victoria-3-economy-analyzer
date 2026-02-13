"""
Victoria 3 Economic Analyzer - GUI Application
Simple graphical interface for non-technical users
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import sys
import os
from pathlib import Path
import queue

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_extractor import EconomicExtractor
from save_monitor import SaveMonitor
from visualizer import EconomicVisualizer


class AnalyzerGUI:
    """GUI for Victoria 3 Economic Analyzer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Victoria 3 Economic Analyzer")
        self.root.geometry("900x700")
        
        # Variables
        self.save_directory = tk.StringVar()
        self.monitoring = False
        self.monitor_thread = None
        self.output_queue = queue.Queue()
        
        # Components
        self.monitor = None
        self.visualizer = None
        
        # Set default save directory
        default_save_dir = self._get_default_save_dir()
        if default_save_dir:
            self.save_directory.set(default_save_dir)
        
        self._create_widgets()
        self._check_output_queue()
        
    def _get_default_save_dir(self):
        """Try to find default Victoria 3 save directory"""
        if os.name == 'nt':  # Windows
            import os
            user_profile = os.environ.get('USERPROFILE', '')
            save_dir = os.path.join(
                user_profile, 
                'Documents', 
                'Paradox Interactive', 
                'Victoria 3', 
                'save games'
            )
            if os.path.exists(save_dir):
                return save_dir
        return ""
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Title
        title = ttk.Label(
            main_frame, 
            text="Victoria 3 Economic Analyzer",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Subtitle
        subtitle = ttk.Label(
            main_frame,
            text="Track overproduction, price crashes, and market dynamics",
            font=('Arial', 10)
        )
        subtitle.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Save directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Save Game Directory", padding="10")
        dir_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Path:").grid(row=0, column=0, sticky=tk.W)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.save_directory, width=50)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self._browse_directory)
        browse_btn.grid(row=0, column=2, sticky=tk.E)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready to analyze", 
            foreground="green"
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Action buttons frame
        buttons_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        buttons_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create buttons in a grid
        btn_width = 20
        
        self.analyze_btn = ttk.Button(
            buttons_frame, 
            text="📊 Analyze Existing Saves",
            command=self._analyze_saves,
            width=btn_width
        )
        self.analyze_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.monitor_btn = ttk.Button(
            buttons_frame,
            text="▶️ Start Monitoring",
            command=self._toggle_monitoring,
            width=btn_width
        )
        self.monitor_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.visualize_btn = ttk.Button(
            buttons_frame,
            text="📈 Generate Charts",
            command=self._generate_visualizations,
            width=btn_width
        )
        self.visualize_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.status_btn = ttk.Button(
            buttons_frame,
            text="ℹ️ Show Status",
            command=self._show_status,
            width=btn_width
        )
        self.status_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.open_viz_btn = ttk.Button(
            buttons_frame,
            text="📁 Open Charts Folder",
            command=self._open_visualizations_folder,
            width=btn_width
        )
        self.open_viz_btn.grid(row=1, column=1, padx=5, pady=5)
        
        self.reset_btn = ttk.Button(
            buttons_frame,
            text="🔄 Reset Data",
            command=self._reset_data,
            width=btn_width
        )
        self.reset_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Output console
        console_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        console_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        console_frame.rowconfigure(0, weight=1)
        console_frame.columnconfigure(0, weight=1)
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Courier', 9)
        )
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear console button
        clear_btn = ttk.Button(
            console_frame,
            text="Clear Output",
            command=self._clear_console
        )
        clear_btn.grid(row=1, column=0, pady=(5, 0))
        
        # Footer
        footer = ttk.Label(
            main_frame,
            text="For The Great Revision Mod Team | v1.0",
            font=('Arial', 8),
            foreground="gray"
        )
        footer.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        # Initial message
        self._log("Welcome to Victoria 3 Economic Analyzer!")
        self._log("Select your save games directory and click an action to begin.")
        self._log("=" * 80)
    
    def _browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(
            title="Select Victoria 3 Save Games Directory",
            initialdir=self.save_directory.get()
        )
        if directory:
            self.save_directory.set(directory)
            self._log(f"Selected directory: {directory}")
    
    def _log(self, message):
        """Add message to console"""
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.root.update_idletasks()
    
    def _clear_console(self):
        """Clear console output"""
        self.console.delete(1.0, tk.END)
    
    def _validate_directory(self):
        """Check if save directory exists"""
        save_dir = self.save_directory.get()
        if not save_dir:
            messagebox.showerror("Error", "Please select a save games directory first!")
            return False
        
        if not os.path.exists(save_dir):
            messagebox.showerror("Error", f"Directory not found:\n{save_dir}")
            return False
        
        return True
    
    def _initialize_components(self):
        """Initialize monitor and visualizer"""
        save_dir = self.save_directory.get()
        
        if not self.monitor or self.monitor.save_directory != Path(save_dir):
            self.monitor = SaveMonitor(save_dir, data_output_dir="./data")
        
        if not self.visualizer:
            self.visualizer = EconomicVisualizer(output_dir="./visualizations")
    
    def _process_save_callback(self, save_file, playthrough_id):
        """Callback for processing saves"""
        try:
            self._log(f"Processing: {save_file.name}")
            
            extractor = EconomicExtractor(str(save_file))
            data = extractor.extract_all()
            
            # Log summary
            crashes = len(data.get('price_crashes', []))
            overproduction = len(data.get('overproduction_ratio', {}))
            date = data.get('metadata', {}).get('date', 'Unknown')
            
            self._log(f"  Date: {date}")
            self._log(f"  Price crashes: {crashes}")
            self._log(f"  Overproduction issues: {overproduction}")
            self._log("-" * 60)
            
            return data
            
        except Exception as e:
            self._log(f"Error processing {save_file.name}: {e}")
            return None
    
    def _analyze_saves(self):
        """Analyze all existing saves"""
        if not self._validate_directory():
            return
        
        self._set_status("Analyzing saves...", "blue")
        self._log("\n[Analyzing Existing Saves]")
        self._log("=" * 80)
        
        def analyze():
            try:
                self._initialize_components()
                count = self.monitor.process_new_saves(self._process_save_callback)
                
                self.output_queue.put(("status", f"Processed {count} saves", "green"))
                self.output_queue.put(("log", f"\nProcessed {count} save files"))
                
                if count > 0:
                    self.output_queue.put(("log", "Generating visualizations..."))
                    self._generate_visualizations_internal()
                    self.output_queue.put(("log", "✓ Analysis complete!"))
                else:
                    self.output_queue.put(("log", "No new saves to process"))
                
            except Exception as e:
                self.output_queue.put(("status", f"Error: {e}", "red"))
                self.output_queue.put(("log", f"Error during analysis: {e}"))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _toggle_monitoring(self):
        """Start or stop monitoring"""
        if not self.monitoring:
            self._start_monitoring()
        else:
            self._stop_monitoring()
    
    def _start_monitoring(self):
        """Start real-time monitoring"""
        if not self._validate_directory():
            return
        
        self.monitoring = True
        self.monitor_btn.config(text="⏸️ Stop Monitoring")
        self._set_status("Monitoring for new saves...", "blue")
        self._log("\n[Starting Real-Time Monitoring]")
        self._log("Checking for new saves every 60 seconds")
        self._log("Click 'Stop Monitoring' to stop and generate visualizations")
        self._log("=" * 80)
        
        def monitor_loop():
            self._initialize_components()
            
            while self.monitoring:
                try:
                    count = self.monitor.process_new_saves(self._process_save_callback)
                    
                    if count > 0:
                        self.output_queue.put(("log", f"\n✓ Processed {count} new save(s)"))
                    
                    # Sleep in small chunks to allow stopping
                    for _ in range(60):
                        if not self.monitoring:
                            break
                        import time
                        time.sleep(1)
                        
                except Exception as e:
                    self.output_queue.put(("log", f"Error during monitoring: {e}"))
                    break
            
            # Monitoring stopped
            self.output_queue.put(("log", "\n[Monitoring Stopped]"))
            self.output_queue.put(("log", "Generating final visualizations..."))
            self._generate_visualizations_internal()
            self.output_queue.put(("status", "Monitoring stopped", "green"))
            self.output_queue.put(("log", "✓ Done! Check the visualizations folder."))
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.monitor_btn.config(text="▶️ Start Monitoring")
        self._log("\nStopping monitoring...")
    
    def _generate_visualizations(self):
        """Generate visualizations button"""
        if not self._validate_directory():
            return
        
        self._set_status("Generating visualizations...", "blue")
        self._log("\n[Generating Visualizations]")
        self._log("=" * 80)
        
        def generate():
            try:
                self._generate_visualizations_internal()
                self.output_queue.put(("status", "Visualizations generated", "green"))
                self.output_queue.put(("log", "\n✓ All visualizations generated!"))
                self.output_queue.put(("log", "Check the './visualizations' folder"))
            except Exception as e:
                self.output_queue.put(("status", f"Error: {e}", "red"))
                self.output_queue.put(("log", f"Error generating visualizations: {e}"))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _generate_visualizations_internal(self):
        """Internal visualization generation (called from threads)"""
        self._initialize_components()
        
        playthroughs = self.monitor.get_all_playthroughs()
        
        if not playthroughs:
            self.output_queue.put(("log", "No playthrough data available yet"))
            return
        
        # Generate for each playthrough
        for playthrough_id in playthroughs:
            data = self.monitor.load_playthrough_data(playthrough_id)
            
            if len(data) < 2:
                self.output_queue.put(("log", f"Skipping {playthrough_id}: need at least 2 data points"))
                continue
            
            self.output_queue.put(("log", f"\nGenerating charts for: {playthrough_id}"))
            
            key_goods = ['grain', 'iron', 'coal', 'steel', 'tools', 'fabric', 
                        'clothes', 'furniture', 'transportation']
            
            self.visualizer.generate_all_visualizations(data, playthrough_id, key_goods)
            self.output_queue.put(("log", f"✓ Charts saved for {playthrough_id}"))
        
        # Generate comparison if multiple playthroughs
        if len(playthroughs) > 1:
            self.output_queue.put(("log", "\nGenerating comparison dashboard..."))
            comparison_data = {}
            for playthrough_id in playthroughs:
                data = self.monitor.load_playthrough_data(playthrough_id)
                if len(data) >= 2:
                    comparison_data[playthrough_id] = data
            
            if comparison_data:
                self.visualizer.plot_comparison_dashboard(comparison_data)
                self.output_queue.put(("log", "✓ Comparison dashboard saved"))
    
    def _show_status(self):
        """Show current tracking status"""
        if not self._validate_directory():
            return
        
        self._initialize_components()
        
        self._log("\n[Current Status]")
        self._log("=" * 80)
        
        playthroughs = self.monitor.get_all_playthroughs()
        self._log(f"Playthroughs tracked: {len(playthroughs)}")
        
        for playthrough_id in playthroughs:
            data = self.monitor.load_playthrough_data(playthrough_id)
            self._log(f"\n  {playthrough_id}:")
            self._log(f"    - Data points: {len(data)}")
            
            if data:
                first_date = data[0].get('metadata', {}).get('date', 'Unknown')
                last_date = data[-1].get('metadata', {}).get('date', 'Unknown')
                self._log(f"    - Date range: {first_date} to {last_date}")
                
                latest = data[-1]
                crashes = latest.get('price_crashes', [])
                overproduction = latest.get('overproduction_ratio', {})
                
                self._log(f"    - Latest snapshot:")
                self._log(f"      • Price crashes: {len(crashes)}")
                self._log(f"      • Overproduction issues: {len(overproduction)}")
        
        self._log("=" * 80)
        
        if not playthroughs:
            self._log("\nNo playthroughs tracked yet. Run 'Analyze Existing Saves' to start.")
    
    def _open_visualizations_folder(self):
        """Open visualizations folder in file explorer"""
        viz_dir = os.path.abspath("./visualizations")
        
        if not os.path.exists(viz_dir):
            messagebox.showinfo("Info", "No visualizations folder yet.\nGenerate some charts first!")
            return
        
        # Open folder based on OS
        if os.name == 'nt':  # Windows
            os.startfile(viz_dir)
        elif sys.platform == 'darwin':  # macOS
            os.system(f'open "{viz_dir}"')
        else:  # Linux
            os.system(f'xdg-open "{viz_dir}"')
        
        self._log(f"Opened folder: {viz_dir}")
    
    def _reset_data(self):
        """Reset all tracking data"""
        result = messagebox.askyesno(
            "Confirm Reset",
            "This will delete all tracked data and start fresh.\n\nAre you sure?"
        )
        
        if result:
            self._initialize_components()
            self.monitor.reset()
            self._log("\n[Data Reset]")
            self._log("All tracking data has been cleared")
            self._log("=" * 80)
            self._set_status("Data reset complete", "green")
    
    def _set_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
    
    def _check_output_queue(self):
        """Check for messages from worker threads"""
        try:
            while True:
                msg_type, *args = self.output_queue.get_nowait()
                
                if msg_type == "log":
                    self._log(args[0])
                elif msg_type == "status":
                    self._set_status(args[0], args[1] if len(args) > 1 else "black")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._check_output_queue)


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set icon if available
    # root.iconbitmap('icon.ico')  # Add if you create an icon
    
    app = AnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
