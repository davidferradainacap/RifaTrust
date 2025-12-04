"""
Vista de prueba simple para verificar que Django funciona
"""
from django.http import HttpResponse
from django.views import View
import datetime

class TestView(View):
    def get(self, request):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test - RifaTrust</title>
            <style>
                body {{
                    font-family: Arial;
                    text-align: center;
                    margin-top: 100px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .box {{
                    background: white;
                    color: #333;
                    padding: 40px;
                    border-radius: 10px;
                    display: inline-block;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                }}
                h1 {{ color: #667eea; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h1>✓ Django + PyMySQL + IIS Funcionando</h1>
                <p><strong>Hora del servidor:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Python:</strong> Activo</p>
                <p><strong>Django:</strong> Activo</p>
                <p><strong>Base de datos:</strong> MySQL (PyMySQL)</p>
                <hr>
                <p><a href="/" style="color: #667eea;">Ir a la página principal</a></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
