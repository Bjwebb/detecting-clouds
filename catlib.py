import pandas

def parse_cat(file_name):
    try:
        df = pandas.read_csv(file_name, delim_whitespace=True, comment='#', header=None, skiprows=11)
    except ZeroDivisionError:
        # This is thrown if there are no lines in the file
        return None

    # Exclude object larger than 10 pixels
    df = df[ (df[7]-df[5]) < 20 ]
    df = df[ (df[8]-df[6]) < 20 ]

    return pandas.DataFrame({ 'x': df[9],
                              'y': df[10],
                              'flux': df[3],
                              'x_min': df[5],
                              'y_min': df[6],
                              'width': df[7]-df[5],
                              'height': df[8]-df[6]
                            })
