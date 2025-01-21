from flask import Flask, render_template # type: ignore
from nbconvert import HTMLExporter # type: ignore
import nbformat # type: ignore
import os

app = Flask(__name__)

notebook_mapping = {
    "tree": "3501_Arboles_De_Desicion.ipynb",
    "new": "3501_Fraudes.ipynb",
}

# Ruta a la carpeta de notebooks
notebooks_folder = "notebooks"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/notebook/<notebook_name>")
def render_notebook(notebook_name):
    if notebook_name not in notebook_mapping:
        return f"<p>NOTEBOOK '{notebook_name}' NO ENCONTRADO.</p>", 404

    notebook_path = os.path.join(notebooks_folder, notebook_mapping[notebook_name])

    if not os.path.exists(notebook_path):
        return f"<p>NOTEBOOK '{notebook_path}' NO EXISTENTE.</p>", 404

    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook_content = nbformat.read(f, as_version=4)

        filtered_cells = []

        if notebook_name == "tree":
            # Mostrar solo las dos primeras gráficas y la gráfica del árbol de decisiones
            graphical_cells = []
            decision_tree_cell = None

            for cell in notebook_content.cells:
                if cell.cell_type == 'code':
                    # Identificar celdas con imágenes
                    for output in cell.get('outputs', []):
                        if 'image/png' in output.get('data', {}):
                            graphical_cells.append(cell)
                            break

                    # Identificar celda del árbol de decisiones
                    if "export_graphviz" in cell['source'] and "Source.from_file" in cell['source']:
                        decision_tree_cell = cell

                if len(graphical_cells) == 2:
                    break

            # Eliminar el código de las celdas seleccionadas
            for cell in graphical_cells:
                cell['source'] = ''

            if decision_tree_cell:
                decision_tree_cell['source'] = ''
                graphical_cells.append(decision_tree_cell)

            filtered_cells = graphical_cells

        elif notebook_name == "new":
            # Mostrar las dos primeras gráficas y la última celda con resultados del modelo matemático
            graphical_cells = []
            last_cell = None

            # Obtener las dos primeras gráficas
            for cell in notebook_content.cells:
                if cell.cell_type == 'code':
                    for output in cell.get('outputs', []):
                        if 'image/png' in output.get('data', {}):
                            graphical_cells.append(cell)
                            break
                if len(graphical_cells) == 2:
                    break

            # Obtener la última celda con resultados
            for cell in reversed(notebook_content.cells):
                if cell.cell_type == 'code' and cell.get('outputs', []):
                    last_cell = cell
                    break

            # Eliminar el código de las celdas seleccionadas
            for cell in graphical_cells:
                cell['source'] = ''
            if last_cell:
                last_cell['source'] = ''

            # Combinar las celdas gráficas y la última celda de resultados
            filtered_cells = graphical_cells + ([last_cell] if last_cell else [])

        # Crear un nuevo notebook con las celdas filtradas
        notebook_content.cells = filtered_cells

        # Usar nbconvert para convertir el notebook filtrado a HTML
        html_exporter = HTMLExporter()
        body, resources = html_exporter.from_notebook_node(notebook_content)

        return body

    except Exception as e:
        return f"<p>RENDERIZACIÓN ERRONEA: {str(e)}</p>", 500

if __name__ == "__main__":
    app.run(debug=True)
