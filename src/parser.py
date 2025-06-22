class SyntaxParser:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self.ast = []
        self.current_token_index = 0
        
    def parse(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []
        self.ast = []
        
        try:
            while not self.is_at_end():
                if self.match('TYPE'):
                    if self.check('IDENTIFIER') and self.lookahead(1, 'DELIMITER', '('):
                        self.parse_function()
                    else:
                        self.parse_declaration()
                elif self.match('KEYWORD'):
                    self.parse_statement()
                elif self.match('PREPROCESSOR'):
                    self.advance()  # Skip preprocessor directives
                elif self.match('DELIMITER', '{') or self.match('DELIMITER', '}'):
                    self.advance()  # Skip braces for now
                else:
                    self.advance()
                    
            return self.ast
        except ParseError as e:
            self.errors.append(str(e))
            return None
            
    def parse_function(self):
        return_type = self.previous()['value']
        func_name = self.advance()['value']  # Function name
        
        # Add function to symbol table
        self.symbol_table.add_symbol(func_name, "function", return_type)
        
        # Parse parameters
        self.consume('DELIMITER', '(')
        params = []
        while not self.check('DELIMITER', ')'):
            if self.match('TYPE'):
                param_type = self.previous()['value']
                param_name = self.advance()['value'] if self.match('IDENTIFIER') else None
                params.append((param_type, param_name))
                if self.match('DELIMITER', ','):
                    continue
        self.consume('DELIMITER', ')')
        
        # Parse function body
        self.consume('DELIMITER', '{')
        body = []
        while not self.check('DELIMITER', '}'):
            if self.match('TYPE'):
                self.parse_declaration()
            elif self.match('KEYWORD'):
                self.parse_statement()
            else:
                self.advance()
        self.consume('DELIMITER', '}')
        
        self.ast.append(('function', return_type, func_name, params, body))
        return True
        
    def parse_declaration(self):
        token = self.previous()
        var_type = token['value']
        
        if not self.match('IDENTIFIER'):
            self.error("Expected identifier after type")
            return
            
        var_name = self.previous()['value']  # Use previous() since match() advanced
        self.symbol_table.add_symbol(var_name, var_type)
        
        expr = None
        if self.match('OPERATOR', '='):
            expr = self.parse_expression()  # Parse full expression
            
        # Semicolon check MUST come after initialization handling
        if not self.match('DELIMITER', ';'):
            self.error("Expected ';' after declaration")
        
        self.ast.append(('declaration', var_type, var_name, expr))
        return True
        
    def parse_statement(self):
        token = self.previous()
        if token['value'] == 'if':
            self.parse_if_statement()
        elif token['value'] == 'return':
            self.parse_return_statement()
        else:
            # Skip until semicolon for now
            while not self.is_at_end() and not self.match('DELIMITER', ';'):
                self.advance()
                
    def parse_return_statement(self):
        expr = None
        if not self.check('DELIMITER', ';'):
            expr = self.parse_expression()
            
        if not self.match('DELIMITER', ';'):
            self.error("Expected ';' after return statement")
            
        self.ast.append(('return', expr))
                
    def parse_if_statement(self):
        self.consume('DELIMITER', '(')
        condition = self.parse_expression()
        self.consume('DELIMITER', ')')
        
        # Parse if body
        if self.match('DELIMITER', '{'):
            body = []
            while not self.check('DELIMITER', '}'):
                if self.match('TYPE'):
                    self.parse_declaration()
                elif self.match('KEYWORD'):
                    self.parse_statement()
                else:
                    self.advance()
            self.consume('DELIMITER', '}')
        else:
            self.parse_statement()
            
        # Parse else if present
        else_body = None
        if self.match('KEYWORD', 'else'):
            if self.match('DELIMITER', '{'):
                else_body = []
                while not self.check('DELIMITER', '}'):
                    if self.match('TYPE'):
                        self.parse_declaration()
                    elif self.match('KEYWORD'):
                        self.parse_statement()
                    else:
                        self.advance()
                self.consume('DELIMITER', '}')
            else:
                else_body = [self.parse_statement()]
                
        self.ast.append(('if', condition, body, else_body))
        
    def parse_expression(self):
        # Implement proper expression parsing with operator precedence
        return self.parse_assignment()
        
    def parse_assignment(self):
        left = self.parse_equality()
        
        if self.match('OPERATOR', '='):
            value = self.parse_assignment()
            return ('assignment', left, value)
            
        return left
        
    def parse_equality(self):
        expr = self.parse_comparison()
        
        while self.match('OPERATOR', '==') or self.match('OPERATOR', '!='):
            op = self.previous()['value']
            right = self.parse_comparison()
            expr = ('binary_op', op, expr, right)
            
        return expr
        
    def parse_comparison(self):
        expr = self.parse_term()
        
        while (self.match('OPERATOR', '<') or 
               self.match('OPERATOR', '>') or 
               self.match('OPERATOR', '<=') or 
               self.match('OPERATOR', '>=')):
            op = self.previous()['value']
            right = self.parse_term()
            expr = ('binary_op', op, expr, right)
            
        return expr
        
    def parse_term(self):
        expr = self.parse_factor()
        
        while self.match('OPERATOR', '+') or self.match('OPERATOR', '-'):
            op = self.previous()['value']
            right = self.parse_factor()
            expr = ('binary_op', op, expr, right)
            
        return expr
        
    def parse_factor(self):
        expr = self.parse_unary()
        
        while self.match('OPERATOR', '*') or self.match('OPERATOR', '/'):
            op = self.previous()['value']
            right = self.parse_unary()
            expr = ('binary_op', op, expr, right)
            
        return expr
        
    def parse_unary(self):
        if self.match('OPERATOR', '!') or self.match('OPERATOR', '-'):
            op = self.previous()['value']
            right = self.parse_unary()
            return ('unary_op', op, right)
            
        return self.parse_primary()
        
    def parse_primary(self):
        if self.match('INTEGER'):
            return ('literal', 'int', self.previous()['value'])
        elif self.match('FLOAT'):
            return ('literal', 'float', self.previous()['value'])
        elif self.match('IDENTIFIER'):
            return ('variable', self.previous()['value'])
        elif self.match('DELIMITER', '('):
            expr = self.parse_expression()
            self.consume('DELIMITER', ')')
            return expr
        else:
            self.error("Expected expression")
            return None
        
    def lookahead(self, offset, token_type, value=None):
        index = self.current_token_index + offset
        if index >= len(self.tokens):
            return False
        token = self.tokens[index]
        if value:
            return token['type'] == token_type and token['value'] == value
        return token['type'] == token_type
        
    def consume(self, token_type, value=None):
        if not self.match(token_type, value):
            self.error(f"Expected '{value}'")
        return self.previous()
        
    # Helper methods
    def advance(self):
        if not self.is_at_end():
            self.current_token_index += 1
        return self.previous()
        
    def previous(self):
        return self.tokens[self.current_token_index - 1]
        
    def check(self, token_type, value=None):
        if self.is_at_end():
            return False
        token = self.tokens[self.current_token_index]
        if value:
            return token['type'] == token_type and token['value'] == value
        return token['type'] == token_type
        
    def match(self, token_type, value=None):
        if self.check(token_type, value):
            self.advance()
            return True
        return False
        
    def is_at_end(self):
        return self.current_token_index >= len(self.tokens)
        
    def error(self, message):
        token = self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else None
        line = token['line'] if token else "EOF"
        col = token['col'] if token else 0
        raise ParseError(f"Syntax error at line {line}, column {col}: {message}")
        
class ParseError(Exception):
    pass