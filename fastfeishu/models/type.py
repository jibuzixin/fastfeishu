class FeiShuCellType:
    def to_json(self):
        return vars(self)

class NotTextLink(FeiShuCellType):
    def __init__(self, link: str):
        self.text = link

class TextLink(FeiShuCellType):
    def __init__(self, link: str, text: str='链接'):
        self.type = 'url'
        self.link = link
        self.text = text

class Email(FeiShuCellType):
    def __init__(self, email: str):
        self.text = email

class Formula(FeiShuCellType):
    def __init__(self, formula: str):
        self.type = 'formula'
        self.text = formula