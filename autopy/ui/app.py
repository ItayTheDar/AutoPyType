import dash
import dash_core_components as dcc
import dash_html_components as html


def create_layout(file1, file2, highlights1, highlights2):
    def highlight_lines(code, highlights):
        lines = code.split('\n')
        highlighted_lines = []
        current_highlight = 0
        current_index = 0
        while current_index < len(lines):
            line = lines[current_index]
            if current_highlight < len(highlights) and \
                    highlights[current_highlight][0] <= current_index + 1 and \
                    current_index + 1 <= highlights[current_highlight][1]:
                highlighted_lines.append({
                    'type': 'code',
                    'props': {
                        'className': 'highlight-line',
                        'style': {'backgroundColor': 'yellow'},
                    },
                    'children': [line],
                })
                if current_index + 1 == highlights[current_highlight][1]:
                    current_highlight += 1
            else:
                highlighted_lines.append(line)
            current_index += 1
        return highlighted_lines

    return html.Div([
        html.Div(className='row', style={'display': 'flex', 'width': '100%'}, children=[
            html.Div(className='six columns', style={'width': '50%'}, children=[
                dcc.Markdown('''
                #### Python File 1
                ''', className='twelve columns', style={'color': '#7F90AC'}),
                dcc.Markdown(f'''
                ```python
                {file1}```
                ''',
                             className='twelve columns', style={'color': '#7F90AC'}),
            ]),
            html.Div(className='six columns', style={'width': '50%'}, children=[
                dcc.Markdown('''
                #### Python File 2
                ''', className='twelve columns', style={'color': '#7F90AC'}),
                dcc.Markdown(f'''
                ```python
                {file1}```
                ''',className='twelve columns', style={'color': '#7F90AC'}),
            ])
        ])
    ])


app = dash.Dash()
exmple = "/Users/itayd/PycharmProjects/AutoPyType/examples/example.py"
example_typed = "/Users/itayd/PycharmProjects/AutoPyType/examples/example_typed.py"
app.layout = create_layout(open(exmple).read(), open(exmple).read(), [(10,29)], [(5,10)])

if __name__ == '__main__':
    app.run_server()
