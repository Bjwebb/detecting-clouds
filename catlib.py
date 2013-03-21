import pandas

def parse_cat(file_name):
    try:
        df = pandas.read_csv(file_name, delim_whitespace=True, comment='#', header=None, skiprows=11)
    except ZeroDivisionError:
        # This is thrown if there are no lines in the file
        return None

    # Exclude object larger than 10 pixels
    df = df[ (df[12]-df[10]) < 20 ]
    df = df[ (df[13]-df[11]) < 20 ]

    return pandas.DataFrame({ 'x': df[14],
                              'y': df[15],
                              'flux': df[4+2],
                              'flux_error': df[4+3],
                              'x_min': df[10],
                              'y_min': df[11],
                              'width': df[12]-df[10],
                              'height': df[13]-df[11]
                            })
