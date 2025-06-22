import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from lexer import LexicalAnalyzer
from parser import SyntaxParser
from semantic import SemanticAnalyzer
from code_gen import CodeGenerator
from symbol_table import SymbolTable

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("C++ Compiler")
        self.root.geometry("1200x850")
        
        # Initialize status variable early
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Configure styles
        self.configure_styles()
        
        # Initialize compiler components
        self.symbol_table = SymbolTable()
        self.lexer = LexicalAnalyzer(self.symbol_table)
        self.parser = SyntaxParser(self.symbol_table)
        self.semantic = SemanticAnalyzer(self.symbol_table)
        self.codegen = CodeGenerator(self.symbol_table)
        
        self.create_widgets()
        self.setup_layout()
        
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main colors
        self.bg_color = "#2e2e2e"
        text_bg = "#1e1e1e"
        text_fg = "#d4d4d4"
        highlight_color = "#3e3e3e"
        
        # Configure styles
        self.root.configure(bg=self.bg_color)
        style.configure('.', background=self.bg_color, foreground=text_fg)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', 
                      background="#3a3a3a", 
                      foreground=text_fg,
                      padding=[10, 5],
                      font=('Segoe UI', 10, 'bold'))  # Increased font size
        style.map('TNotebook.Tab',
                background=[('selected', self.bg_color)],
                foreground=[('selected', 'white')])
        style.configure('TButton', 
                       background="#424242",
                       foreground=text_fg,
                       font=('Segoe UI', 10, 'bold'),  # Increased font size and bold
                       borderwidth=1,
                       relief="raised",
                       padding=8)  # Increased padding
        style.map('TButton',
                 background=[('active', '#4a4a4a'), ('pressed', '#3a3a3a')])
        
    def create_widgets(self):
        # Create main panes
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        
        # Editor frame with line numbers
        self.editor_frame = ttk.Frame(self.main_pane)
        self.editor_container = ttk.Frame(self.editor_frame)
        self.editor_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(self.editor_container, 
                                  width=4, 
                                  padx=4, 
                                  pady=5,
                                  bg="#252526", 
                                  fg="#858585",
                                  state="disabled",
                                  font=("Consolas", 12),
                                  relief="flat",
                                  bd=0)
        self.line_numbers.pack(side="left", fill="y")
        
        # Editor
        self.editor = scrolledtext.ScrolledText(self.editor_container,
                                             wrap=tk.WORD,
                                             font=("Consolas", 12),
                                             bg="#1e1e1e",
                                             fg="#d4d4d4",
                                             insertbackground="white",
                                             selectbackground="#264f78",
                                             padx=10,
                                             pady=5,
                                             undo=True)
        self.editor.pack(side="left", fill="both", expand=True)
        
        # Add sample code
        self.editor.insert(tk.END, 
            "#include <iostream>\n\n"
            "int main() {\n"
            "    int x = 5;\n"
            "    float y = 3.14;\n"
            "    if (x > 0) {\n"
            "        x = x * 2;\n"
            "    }\n"
            "    return 0;\n"
            "}")
        
        # Output notebook
        self.notebook = ttk.Notebook(self.main_pane)
        
        # Tokens tab
        self.tokens_frame = ttk.Frame(self.notebook)
        self.tokens_text = scrolledtext.ScrolledText(self.tokens_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    bg="#1e1e1e",
                                                    fg="#d4d4d4")
        self.tokens_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # AST tab
        self.ast_frame = ttk.Frame(self.notebook)
        self.ast_text = scrolledtext.ScrolledText(self.ast_frame, 
                                                wrap=tk.WORD, 
                                                font=("Consolas", 10),
                                                bg="#1e1e1e",
                                                fg="#d4d4d4")
        self.ast_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Symbol Table tab
        self.symtab_frame = ttk.Frame(self.notebook)
        self.symtab_text = scrolledtext.ScrolledText(self.symtab_frame, 
                                                   wrap=tk.WORD, 
                                                   font=("Consolas", 10),
                                                   bg="#1e1e1e",
                                                   fg="#d4d4d4")
        self.symtab_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Generated Code tab
        self.code_frame = ttk.Frame(self.notebook)
        self.code_text = scrolledtext.ScrolledText(self.code_frame, 
                                                 wrap=tk.WORD, 
                                                 font=("Consolas", 10),
                                                 bg="#1e1e1e",
                                                 fg="#d4d4d4")
        self.code_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Messages tab
        self.msg_frame = ttk.Frame(self.notebook)
        self.msg_text = scrolledtext.ScrolledText(self.msg_frame, 
                                                wrap=tk.WORD, 
                                                font=("Consolas", 10),
                                                bg="#1e1e1e",
                                                fg="#d4d4d4")
        self.msg_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add tabs to notebook
        self.notebook.add(self.tokens_frame, text="Tokens")
        self.notebook.add(self.ast_frame, text="AST")
        self.notebook.add(self.symtab_frame, text="Symbol Table")
        self.notebook.add(self.code_frame, text="Generated Code")
        self.notebook.add(self.msg_frame, text="Messages")
        
        # Control buttons with larger font
        self.control_frame = ttk.Frame(self.root)
        self.compile_btn = ttk.Button(self.control_frame, text="Compile (F5)", command=self.compile, style='TButton')
        self.run_btn = ttk.Button(self.control_frame, text="Run (F6)", command=self.run, style='TButton')
        self.clear_btn = ttk.Button(self.control_frame, text="Clear All", command=self.clear, style='TButton')
        
        # Button layout
        self.compile_btn.pack(side="left", padx=10, pady=10)  # Increased padding
        self.run_btn.pack(side="left", padx=10, pady=10)
        self.clear_btn.pack(side="right", padx=10, pady=10)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, 
                                  textvariable=self.status_var,
                                  relief="sunken",
                                  anchor="w",
                                  padding=(10, 5),
                                  background="#3a3a3a",
                                  foreground="#b0b0b0",
                                  font=('Segoe UI', 10))  # Increased font size
        
        # Update line numbers after all widgets are created
        self.update_line_numbers()
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        
    def setup_layout(self):
        # Add frames to main pane
        self.main_pane.add(self.editor_frame, weight=40)
        self.main_pane.add(self.notebook, weight=60)
        self.main_pane.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control and status bars
        self.control_frame.pack(fill="x", padx=10, pady=(0, 10))  # Increased padding
        self.status_bar.pack(fill="x", side="bottom")
        
    def update_line_numbers(self, event=None):
        lines = self.editor.get("1.0", "end-1c").split("\n")
        line_count = len(lines)
        
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, line_count + 1)))
        self.line_numbers.config(state="disabled")
        
        # Update cursor position in status bar
        cursor_pos = self.editor.index(tk.INSERT)
        self.status_var.set(f"Line: {cursor_pos.split('.')[0]}, Column: {cursor_pos.split('.')[1]} | Ready")
        
    def change_background_color(self, success):
        """Change background color based on compilation status"""
        if success:
            self.root.configure(bg="#2e5e2e")  # Dark green for success
            self.status_bar.configure(background="#3e7e3e", foreground="#ffffff")
        else:
            self.root.configure(bg="#5e2e2e")  # Dark red for errors
            self.status_bar.configure(background="#7e3e3e", foreground="#ffffff")
        
        # Reset after 3 seconds
        self.root.after(3000, self.reset_background_color)
        
    def reset_background_color(self):
        """Reset background to default"""
        self.root.configure(bg=self.bg_color)
        self.status_bar.configure(background="#3a3a3a", foreground="#b0b0b0")
        
    def compile(self):
        source = self.editor.get("1.0", tk.END)
        
        # Clear previous results
        self.tokens_text.delete("1.0", tk.END)
        self.ast_text.delete("1.0", tk.END)
        self.symtab_text.delete("1.0", tk.END)
        self.code_text.delete("1.0", tk.END)
        self.msg_text.delete("1.0", tk.END)
        
        # Reset symbol table
        self.symbol_table = SymbolTable()
        self.lexer.symbol_table = self.symbol_table
        self.parser.symbol_table = self.symbol_table
        self.semantic.symbol_table = self.symbol_table
        self.codegen.symbol_table = self.symbol_table
        
        # Lexical analysis
        tokens = self.lexer.tokenize(source)
        self.tokens_text.insert(tk.END, "\n".join(
            f"{token['line']}:{token['col']} \t{token['type']} \t'{token['value']}'"
            for token in tokens
        ))
        
        # Syntax analysis
        ast = self.parser.parse(tokens)
        if ast:
            self.ast_text.insert(tk.END, "\n".join(str(node) for node in ast))
        else:
            self.msg_text.insert(tk.END, "Syntax errors detected!\n")
            
        # Semantic analysis
        if ast and self.semantic.analyze(ast):
            self.msg_text.insert(tk.END, "Semantic analysis passed\n")
        else:
            self.msg_text.insert(tk.END, "Semantic errors detected!\n")
            
        # Show symbol table
        self.symtab_text.insert(tk.END, str(self.symbol_table))
        
        # Code generation
        if ast and not self.parser.errors and not self.semantic.errors:
            code = self.codegen.generate(ast)
            self.code_text.insert(tk.END, code)
            self.msg_text.insert(tk.END, "Code generation successful!\n")
            
        # Display errors
        for error in self.lexer.errors + self.parser.errors + self.semantic.errors:
            self.msg_text.insert(tk.END, error + "\n")
            
        for warning in self.semantic.warnings:
            self.msg_text.insert(tk.END, "WARNING: " + warning + "\n")
            
        # Update status and background color
        has_errors = self.lexer.errors or self.parser.errors or self.semantic.errors
        if not has_errors:
            self.status_var.set("Compilation successful")
            self.change_background_color(True)
        else:
            self.status_var.set("Compilation completed with errors")
            self.change_background_color(False)
            
    def run(self):
        self.status_var.set("Running program...")
        self.root.update()
        # Simulated execution delay
        self.root.after(1500, lambda: self.status_var.set("Execution completed"))
        messagebox.showinfo("Execution", "Code executed successfully (simulated)")
        
    def clear(self):
        self.editor.delete("1.0", tk.END)
        self.tokens_text.delete("1.0", tk.END)
        self.ast_text.delete("1.0", tk.END)
        self.symtab_text.delete("1.0", tk.END)
        self.code_text.delete("1.0", tk.END)
        self.msg_text.delete("1.0", tk.END)
        self.status_var.set("Cleared all content")
        self.update_line_numbers()
        self.reset_background_color()

if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()