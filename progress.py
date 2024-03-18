def progress_bar_once(word, percentage = None, num = 30, ascii = "┄", title = False):
    if title:
        S1 = word.center(num, "=")
        return S1
    else:
        S1 = word.center(num, ascii)
        if percentage: return "├" + S1 + "→  " + str(percentage) + '%'
        else:
            return "├" + S1 + "→  "