class RequestError(Exception):
    def __init__(self, html, code):
        self.html = html
        self.code = code
    
    def __str__(self):
        return f'Status code: {self.code} - HTML: {html}'
