def format_title(title, row_len, sep):
    rem = row_len - len(title)  # How many spaces available?
    left = (rem//2) * sep
    right = (rem-len(left)) * sep
    return '{}{}{}'.format(left, title, right)


def get_widest_cols(data):
    # Get number of columns and rows
    num_rows = len(data)
    num_cols = len(data[0])
    # Get largest row of each column and store in list
    widest_cols = []
    for col in range(num_cols):
        widest = 0
        for row in range(num_rows):
            cell = str(data[row][col])
            widest = max(len(cell), widest)
        widest_cols.append(widest)
    return widest_cols


# Help from https://stackoverflow.com/a/9536084/4522767
def create_table(data, title, col_sep=' | ', row_sep_tag='-', out_pad=2):
    # Get data measurements
    num_cols = len(data[0])
    num_rows = len(data)
    # Get the widest cell in each column
    col_widths = get_widest_cols(data)
    # Create table to fill with data
    table = []
    # Fill table with data
    for r in range(num_rows):
        data_row = data[r]
        row = []
        for c in range(num_cols):
            data_cell = data_row[c]
            # Create a template for this cell and use col width so all cells
            # in columns have same width
            template = '{{:{}}}'.format(col_widths[c])
            # Append cell to row
            row.append(template.format(data_cell))
        # Append row to table, adding space before and after row and
        # using column seperator between cells
        table.append(' {} '.format(col_sep.join(row)))
    # Get width of table
    table_width = len(table[0])
    # Add row seperators
    row_sep = '\n{}\n'.format(row_sep_tag * (table_width))
    table = row_sep.join(table)
    # Prepend title to top of table
    title = format_title(title, table_width, row_sep_tag)
    table = '{}\n\n{}'.format(title, table)
    # Add padding above and below table
    table = '{1}{0}{1}'.format(table, '\n'*out_pad)
    return table
