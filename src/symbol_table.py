class SymbolTable:
    def __init__(self):
        self.table = []
        self.scope_stack = [{"name": "global", "level": 0}]
        
    def enter_scope(self, scope_name):
        level = len(self.scope_stack)
        self.scope_stack.append({"name": scope_name, "level": level})
        
    def exit_scope(self):
        if len(self.scope_stack) > 1:
            # Remove all symbols from current scope
            scope_name = self.current_scope()["name"]
            self.table = [entry for entry in self.table if entry['scope'] != scope_name]
            self.scope_stack.pop()
            
    def current_scope(self):
        return self.scope_stack[-1]
    
    def add_symbol(self, name, symbol_type, value=None):
        current_scope = self.current_scope()["name"]
        
        # Check for existing symbol in current scope
        for entry in self.table:
            if entry['name'] == name and entry['scope'] == current_scope:
                return  # Skip duplicate
                
        self.table.append({
            'name': name,
            'type': symbol_type,
            'value': value,
            'scope': current_scope
        })
        
    def lookup(self, name):
        # Search from current scope outwards
        for scope in reversed(self.scope_stack):
            scope_name = scope["name"]
            for entry in reversed(self.table):
                if entry['name'] == name and entry['scope'] == scope_name:
                    return entry
        return None
        
    def update_value(self, name, value):
        symbol = self.lookup(name)
        if symbol:
            symbol['value'] = value
            return True
        return False
        
    def __str__(self):
        headers = ["Name", "Type", "Value", "Scope"]
        rows = [headers]
        for entry in self.table:
            rows.append([
                entry['name'],
                entry['type'],
                str(entry['value']),
                entry['scope']
            ])
        
        # Format as table
        col_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]
        output = ""
        for row in rows:
            output += " | ".join(str(item).ljust(width) for item, width in zip(row, col_widths)) + "\n"
        return output