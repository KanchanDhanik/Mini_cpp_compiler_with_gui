import re

class LexicalAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.tokens = []
        self.errors = []
        
    def tokenize(self, source_code):
        self.tokens = []
        self.errors = []
        
        token_specs = [
            ('TYPE', r'\b(int|float|char|bool|double|void)\b'),
            ('KEYWORD', r'\b(if|else|while|for|return|break|continue|class|struct)\b'),
            ('OPERATOR', r'[+\-*/%=!<>&|^~]|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\|'),
            ('DELIMITER', r'[();,{}\[\]\.]'),
            ('IDENTIFIER', r'[a-zA-Z_]\w*'),
            ('FLOAT', r'\d+\.\d+([eE][-+]?\d+)?'),
            ('INTEGER', r'\d+'),
            ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),
            ('CHAR', r"'(\\?.)'"),
            ('PREPROCESSOR', r'#\s*\w+'),
            ('WHITESPACE', r'\s+'),
            ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),
            ('MISMATCH', r'.')
        ]
        
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)
        line_num = 1
        line_start = 0
        
        for mo in re.finditer(tok_regex, source_code):
            kind = mo.lastgroup
            value = mo.group()
            col = mo.start() - line_start
            line = line_num
            
            if kind == 'WHITESPACE':
                if '\n' in value:
                    line_num += value.count('\n')
                    line_start = mo.end()
                continue
            elif kind == 'COMMENT':
                if '\n' in value:
                    line_num += value.count('\n')
                    line_start = mo.end()
                continue
            elif kind == 'MISMATCH':
                self.errors.append(f"Lexical error at line {line}: Unexpected character '{value}'")
                continue
            
            # Add identifiers to symbol table
            if kind == 'IDENTIFIER':
                self.symbol_table.add_symbol(value, "identifier")
                
            self.tokens.append({
                'type': kind,
                'value': value,
                'line': line,
                'col': col
            })
            
        return self.tokens