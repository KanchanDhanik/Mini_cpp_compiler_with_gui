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
        self.root.geometry("1000x800")
        
        # Initialize compiler components
        self.symbol_table = SymbolTable()
        self.lexer = LexicalAnalyzer(self.symbol_table)
        self.parser = SyntaxParser(self.symbol_table)
        self.semantic = SemanticAnalyzer(self.symbol_table)
        self.codegen = CodeGenerator(self.symbol_table)
        
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        
        # Editor tab
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="Editor")
        self.editor = scrolledtext.ScrolledText(self.editor_frame, wrap=tk.WORD, font=("Consolas", 12))
        self.editor.pack(fill="both", expand=True, padx=10, pady=10)
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
        
        # Tokens tab
        self.tokens_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tokens_frame, text="Tokens")
        self.tokens_text = scrolledtext.ScrolledText(self.tokens_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.tokens_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # AST tab
        self.ast_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ast_frame, text="AST")
        self.ast_text = scrolledtext.ScrolledText(self.ast_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.ast_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Symbol Table tab
        self.symtab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.symtab_frame, text="Symbol Table")
        self.symtab_text = scrolledtext.ScrolledText(self.symtab_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.symtab_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Generated Code tab
        self.code_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.code_frame, text="Generated Code")
        self.code_text = scrolledtext.ScrolledText(self.code_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.code_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Messages tab
        self.msg_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.msg_frame, text="Messages")
        self.msg_text = scrolledtext.ScrolledText(self.msg_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.msg_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control buttons
        self.control_frame = ttk.Frame(self.root)
        self.compile_btn = ttk.Button(self.control_frame, text="Compile", command=self.compile)
        self.compile_btn.pack(side="left", padx=5, pady=5)
        self.run_btn = ttk.Button(self.control_frame, text="Run", command=self.run)
        self.run_btn.pack(side="left", padx=5, pady=5)
        self.clear_btn = ttk.Button(self.control_frame, text="Clear", command=self.clear)
        self.clear_btn.pack(side="right", padx=5, pady=5)
        
    def setup_layout(self):
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.control_frame.pack(fill="x", padx=10, pady=5)
        
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
            
    def run(self):
        messagebox.showinfo("Execution", "Code executed successfully (simulated)")
        
    def clear(self):
        self.editor.delete("1.0", tk.END)
        self.tokens_text.delete("1.0", tk.END)
        self.ast_text.delete("1.0", tk.END)
        self.symtab_text.delete("1.0", tk.END)
        self.code_text.delete("1.0", tk.END)
        self.msg_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()