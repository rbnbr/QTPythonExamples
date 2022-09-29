from PySide6.QtGui import QColor


# color tables from: https://github.com/d3/d3-scale-chromatic
color_tables = {
    "category10": "1f77b4ff7f0e2ca02cd627289467bd8c564be377c27f7f7fbcbd2217becf",
    "tableau10": "4e79a7f28e2ce1575976b7b259a14fedc949af7aa1ff9da79c755fbab0ab",
}


def get_available_color_tables():
    """
    Returns the names of the available color tables.
    Can be used as keys in 'get_color_table(name)'
    :return:
    """
    return list(color_tables.keys())


def get_color_table(name: str):
    """
    Returns the color table specified by name as list of QColors.
    :param name:
    :return:
    """
    colors = color_tables[name]
    q_colors = []

    for i in range(int(len(colors) / 6)):
        q_colors.append(QColor("#{}".format(colors[i*6:(i+1)*6])))

    return q_colors
